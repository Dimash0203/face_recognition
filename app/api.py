# app/api.py
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Query
from pydantic import BaseModel, Field

from .config import settings
from .utils import read_image, read_image_b64
from .service import verify_pair
from .models_registry import reset_models

router = APIRouter()


class ResultItem(BaseModel):
    model: str
    lookalike_percent: Optional[int] = None
    same_person: Optional[bool] = None
    error: Optional[str] = None


class VerifyResponse(BaseModel):
    detector_backend: str
    threshold: float
    results: List[ResultItem]


class VerifyB64Request(BaseModel):
    image1_b64: str
    image2_b64: str
    threshold: float = Field(0.7, description="Порог для сравнения (по умолчанию 0.7)")


@router.get("/models", response_model=List[str], summary="Список доступных моделей", tags=["meta"])
def list_models():
    # Всегда ["Facenet"]
    return settings.verification_models


@router.post(
    "/verify",
    response_model=VerifyResponse,
    summary="Сравнить два изображения (multipart/form-data)",
    tags=["verify"],
)
async def verify_multipart(
    image1: UploadFile = File(..., description="Первое изображение (jpeg/png)"),
    image2: UploadFile = File(..., description="Второе изображение (jpeg/png)"),
    threshold: float = Query(0.7, description="Порог для сравнения (по умолчанию 0.7)"),
):
    img1 = read_image(image1)
    img2 = read_image(image2)
    th = threshold if threshold is not None else settings.threshold
    result = verify_pair(img1, img2, settings.verification_models, th)
    return VerifyResponse(**result)


@router.post(
    "/verify-b64",
    response_model=VerifyResponse,
    summary="Сравнить два изображения (base64)",
    tags=["verify"],
)
async def verify_base64(payload: VerifyB64Request):
    img1 = read_image_b64(payload.image1_b64)
    img2 = read_image_b64(payload.image2_b64)
    th = payload.threshold if payload.threshold is not None else settings.threshold
    result = verify_pair(img1, img2, settings.verification_models, th)
    return VerifyResponse(**result)


@router.get("/healthz", summary="Проверка работоспособности", tags=["meta"])
def healthz():
    return {"status": "ok", "app": settings.app_name, "version": settings.version}

@router.post("/admin/reload", summary="Перезагрузить модели (очистить Keras-сессию и кэш)", tags=["admin"])
def admin_reload():
    reset_models()
    # Прогреем снова, чтобы при первом запросе не тратить время
    for name in settings.verification_models:
        from .models_registry import get_model
        get_model(name)
    return {"status": "ok", "message": "Модели перезагружены"}
