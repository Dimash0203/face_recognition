# app/service.py
from __future__ import annotations
from typing import Dict, Any, List
import numpy as np
from deepface import DeepFace
from .config import settings
from .utils import cosine_sim, sim_to_percent, cosine_to_percent
from .models_registry import get_model

def _choose_detector() -> str:
    return settings.primary_detector

def _embedding(img_bgr: np.ndarray, model_name: str, detector_backend: str) -> np.ndarray:
    errors: List[str] = []
    for backend in [detector_backend, settings.fallback_detector, "opencv"]:
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
            return np.array(item["embedding"], dtype=np.float32)
        except Exception as e:
            errors.append(f"{backend}: {e}")
            continue
    raise RuntimeError(" / ".join(errors))

def verify_pair(img1_bgr: np.ndarray, img2_bgr: np.ndarray, model_list: list[str]) -> Dict[str, Any]:
    detector = _choose_detector()
    out: Dict[str, Any] = {
        "detector_backend": detector,
        "threshold": settings.threshold,
        "results": []
    }
    for model_name in model_list:
        try:
            _ = get_model(model_name)
            e1 = _embedding(img1_bgr, model_name, detector)
            e2 = _embedding(img2_bgr, model_name, detector)
            sim = cosine_sim(e1, e2)

            lookalike_percent = cosine_to_percent(sim)
            adjusted = sim_to_percent(sim, settings.percent_low, settings.percent_high)

            out["results"].append({
                "model": model_name,
                "lookalike_percent": lookalike_percent,
                "same_person": bool(sim >= settings.threshold)
            })
        except Exception as e:
            out["results"].append({
                "model": model_name,
                "error": str(e)
            })
    return out
