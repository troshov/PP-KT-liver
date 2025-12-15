import numpy as np
import cv2
import SimpleITK as sitk
from PIL import Image


def load_dicom(file_path: str):
    """
    Загрузка DICOM файла и приведение к 2D-срезу.
    Возвращает нормализованное изображение и исходную форму (H, W).
    """
    reader = sitk.ImageFileReader()
    reader.SetFileName(file_path)
    image = reader.Execute()
    img_array = sitk.GetArrayFromImage(image)  # (Z, H, W) или (H, W)

    if len(img_array.shape) == 3:
        # берём первый срез (или можно заменить на средний)
        img_array = img_array[0]

    img_array = img_array.astype(np.float32)

    img_min = img_array.min()
    img_max = img_array.max()
    if img_max > img_min:
        img_normalized = (img_array - img_min) / (img_max - img_min)
    else:
        img_normalized = img_array - img_min

    return img_normalized, img_array.shape  # (H, W)


def preprocess_for_model(image: np.ndarray):
    """
    Препроцессинг как при обучении liver_model.onnx:
    ресайз до 256x256, стандартизация, добавление batch/канала.
    """
    img_resized = cv2.resize(image, (256, 256), interpolation=cv2.INTER_LINEAR)

    img_mean = np.mean(img_resized)
    img_std = np.std(img_resized)
    if img_std > 0:
        img_normalized = (img_resized - img_mean) / img_std
    else:
        img_normalized = img_resized - img_mean

    # (H, W) -> (1, H, W, 1)
    img_expanded = np.expand_dims(img_normalized, axis=(0, -1)).astype(np.float32)

    return img_expanded


def postprocess_mask(pred_mask: np.ndarray, original_shape, threshold: float = 0.5):
    """
    Постобработка маски: порог, выбор крупнейшей компоненты,
    ресайз до исходного размера.
    pred_mask: (H, W) с вероятностями.
    """
    binary_mask = (pred_mask > threshold).astype(np.uint8)

    num_labels, labels = cv2.connectedComponents(binary_mask)
    if num_labels > 1:
        component_sizes = [np.sum(labels == i) for i in range(1, num_labels)]
        largest_component = np.argmax(component_sizes) + 1
        binary_mask = (labels == largest_component).astype(np.uint8)

    if binary_mask.shape != original_shape:
        binary_mask = cv2.resize(
            binary_mask,
            (original_shape[1], original_shape[0]),
            interpolation=cv2.INTER_NEAREST,
        )

    return binary_mask  # 0/1


def calculate_metrics(mask: np.ndarray):
    """
    Простые метрики по бинарной маске.
    """
    area = int(np.sum(mask > 0))
    # упрощённый пересчёт в объём: считаем толщину среза 2 мм
    volume_mm3 = float(area * 2)
    volume_ml = volume_mm3 / 1000.0
    return {
        "area_pixels": area,
        "volume_mm3": volume_mm3,
        "volume_ml": volume_ml,
    }
