from pathlib import Path
import onnxruntime as ort


def load_model(model_path: str = "weights/liver_model.onnx"):
    """
    Загружает ONNX-модель печени и возвращает onnxruntime сессию
    вместе с именами входа и выхода.
    """
    model_file = Path(model_path)
    if not model_file.exists():
        raise FileNotFoundError(f"Model file not found: {model_file}")

    session = ort.InferenceSession(str(model_file), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    return {
        "session": session,
        "input_name": input_name,
        "output_name": output_name,
    }



