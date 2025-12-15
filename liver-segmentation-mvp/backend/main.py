from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path
from datetime import datetime
from PIL import Image as PILImage
import shutil
import uuid

from models import load_model
from inference import (
    load_dicom,
    preprocess_for_model,
    postprocess_mask,
    calculate_metrics,
)

app = FastAPI(title="Liver Segmentation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
RESULTS_DIR = Path("results")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Загружаем ONNX-модель
model = load_model("weights/liver_model.onnx")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": "ONNX liver_model"}


@app.post("/upload")
async def upload_and_segment(file: UploadFile = File(...)):
    try:
        result_id = str(uuid.uuid4())[:8]
        result_dir = RESULTS_DIR / result_id
        result_dir.mkdir(exist_ok=True)

        file_ext = Path(file.filename).suffix
        file_path = UPLOAD_DIR / f"{result_id}{file_ext}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1) загрузка и препроцессинг
        image, original_shape = load_dicom(str(file_path))  # (H, W)
        input_tensor = preprocess_for_model(image)          # (1, 256, 256, 1)

        # 2) инференс ONNX
        session = model["session"]
        input_name = model["input_name"]
        output_name = model["output_name"]

        outputs = session.run([output_name], {input_name: input_tensor})
        pred = outputs[0]  # ожидаем (1, 256, 256, 1) или подобное
        pred_mask = pred[0, :, :, 0]

        # 3) постпроцессинг
        final_mask = postprocess_mask(pred_mask, original_shape, threshold=0.5)
        mask_uint8 = (final_mask.astype("uint8") * 255)

        metrics = calculate_metrics(final_mask)

        # 4) сохранение маски
        mask_image = PILImage.fromarray(mask_uint8)
        mask_path = result_dir / "mask.png"
        mask_image.save(mask_path)

        # 5) сохранение исходного нормализованного изображения
        orig_uint8 = (image * 255).astype("uint8")
        orig_pil = PILImage.fromarray(orig_uint8)
        original_path = result_dir / "original.png"
        orig_pil.save(original_path)

        return JSONResponse(
            {
                "result_id": result_id,
                "status": "success",
                "mask_url": f"/results/{result_id}/mask.png",
                "original_url": f"/results/{result_id}/original.png",
                "metrics": metrics,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/results/{result_id}/mask.png")
async def get_mask(result_id: str):
    mask_path = RESULTS_DIR / result_id / "mask.png"
    if mask_path.exists():
        return FileResponse(mask_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Mask not found")


@app.get("/results/{result_id}/original.png")
async def get_original(result_id: str):
    original_path = RESULTS_DIR / result_id / "original.png"
    if original_path.exists():
        return FileResponse(original_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Original image not found")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)