# app/service.py
from __future__ import annotations
from typing import Dict, Any, List
import numpy as np
from deepface import DeepFace
from loguru import logger

from app.utils.config import settings
from app.utils.utils_ml import cosine_sim, cosine_to_percent
from app.models.models_registry import get_model, reset_models

RETINAFACE_WEIGHT_NAME = "retinaface.h5"

class FaceProcessError(Exception):
    pass

class FaceNotDetectedError(FaceProcessError):
    def __init__(self, image_idx: int):
        super().__init__(
            f"Лицо не обнаружено на изображении {image_idx}. "
            f"Попробуйте фронтальное фото хорошего качества без сильных затемнений/поворотов."
        )

class ModelUnavailableError(FaceProcessError):
    def __init__(self, model_name: str):
        super().__init__(f"Модель '{model_name}' недоступна. Проверьте наличие весов.")

def _has_retinaface_weight() -> bool:
    cache_dir = settings.deepface_home / ".deepface" / "weights"
    return (cache_dir / RETINAFACE_WEIGHT_NAME).exists()

def _choose_detectors() -> List[str]:
    backends = ["opencv"]
    if _has_retinaface_weight():
        backends.append("retinaface")
    return backends

def _embedding(img_bgr: np.ndarray, model_name: str, image_idx: int) -> np.ndarray:
    last_err = None
    for backend in _choose_detectors():
        try:
            rep = DeepFace.represent(
                img_path=img_bgr,
                model_name=model_name,
                detector_backend=backend,
                align=True,
                enforce_detection=True,
                normalization="base",
            )
            item = rep[0] if isinstance(rep, list) else rep
            emb = np.array(item["embedding"], dtype=np.float32)
            return emb
        except Exception as e:
            last_err = e
            logger.debug("Не удалось получить embedding (detector={}): {}", backend, e)
            continue
    raise FaceNotDetectedError(image_idx=image_idx) from last_err

def _verify_once(img1_bgr: np.ndarray, img2_bgr: np.ndarray, model_list: list[str], threshold: float) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "detector_backend": ",".join(_choose_detectors()),
        "threshold": threshold,
        "results": [],
    }
    for model_name in model_list:
        try:
            # ensure model in cache (и корректный граф TF)
            try:
                _ = get_model(model_name)
            except Exception as e:
                logger.error("Не удалось загрузить модель {}: {}", model_name, e)
                raise ModelUnavailableError(model_name)

            e1 = _embedding(img1_bgr, model_name, image_idx=1)
            e2 = _embedding(img2_bgr, model_name, image_idx=2)

            sim = cosine_sim(e1, e2)
            out["results"].append({
                "model": model_name,
                "lookalike_percent": cosine_to_percent(sim),
                "same_person": bool(sim >= threshold),
            })

        except FaceProcessError as fe:
            out["results"].append({"model": model_name, "error": str(fe)})
        except Exception as e:
            logger.exception("Необработанное исключение в _verify_once: {}", e)
            out["results"].append({"model": model_name, "error": "Внутренняя ошибка обработки изображения."})
    return out

def verify_pair(img1_bgr: np.ndarray, img2_bgr: np.ndarray, model_list: list[str], threshold: float) -> Dict[str, Any]:
    """
    Обёртка с авто-восстановлением: при неожиданных ошибках пробуем один раз
    очистить Keras-сессию и кэш моделей, затем повторить.
    """
    result = _verify_once(img1_bgr, img2_bgr, model_list, threshold)
    # Если в любом элементе results — «Внутренняя ошибка ...», попробуем авто-reset и повтор
    need_retry = any(item.get("error") == "Внутренняя ошибка обработки изображения." for item in result["results"])
    if need_retry:
        logger.warning("Обнаружены внутренние ошибки — выполняем reset_models и повтор")
        reset_models()
        result = _verify_once(img1_bgr, img2_bgr, model_list, threshold)
    return result
