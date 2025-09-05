# app/utils.py
import base64
import re
import numpy as np
from numpy.linalg import norm
from fastapi import UploadFile, HTTPException
import cv2
from .config import settings

ALLOWED_MIME = {"image/jpeg", "image/png", "image/jpg"}
DATA_URL_RE = re.compile(r"^data:(image/\w+);base64,(.+)$", re.IGNORECASE)

def read_image(file: UploadFile) -> np.ndarray:
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(415, detail=f"Unsupported content type: {file.content_type}")
    data = file.file.read(settings.max_image_bytes + 1)
    if len(data) == 0:
        raise HTTPException(400, detail="Empty file")
    if len(data) > settings.max_image_bytes:
        raise HTTPException(413, detail=f"File too large (>{settings.max_image_bytes} bytes)")
    img_array = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, detail="Cannot decode image")
    return img

def read_image_b64(b64: str) -> np.ndarray:
    m = DATA_URL_RE.match(b64.strip())
    if m:
        mime, payload = m.groups()
        if mime.lower() not in ALLOWED_MIME:
            raise HTTPException(415, detail=f"Unsupported content type in data URL: {mime}")
        b64_bytes = payload.encode("utf-8")
    else:
        b64_bytes = b64.encode("utf-8")

    try:
        raw = base64.b64decode(b64_bytes, validate=True)
    except Exception:
        raise HTTPException(400, detail="Invalid base64 image")

    if len(raw) == 0:
        raise HTTPException(400, detail="Empty base64 payload")
    if len(raw) > settings.max_image_bytes:
        raise HTTPException(413, detail=f"File too large (>{settings.max_image_bytes} bytes)")

    img_array = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, detail="Cannot decode base64 image")
    return img

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (norm(a) * norm(b)))

def sim_to_percent(sim: float, low: float, high: float) -> int:
    sim = max(min(sim, high), low)
    return int(round((sim - low) / (high - low) * 100))

def cosine_to_percent(sim: float) -> int:
    return int(round(max(0.0, min(1.0, sim)) * 100))
