# app/api.py
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from .config import settings
from .utils import read_image, read_image_b64
from .service import verify_pair

router = APIRouter()

class ResultItem(BaseModel):
    model: str
    lookalike_percent: Optional[int] = None
    # adjusted_lookalike_percent: Optional[int] = None
    same_person: Optional[bool] = None
    error: Optional[str] = None

class VerifyResponse(BaseModel):
    detector_backend: str
    threshold: float
    results: List[ResultItem]

class VerifyB64Request(BaseModel):
    image1_b64: str
    image2_b64: str

@router.get("/models", response_model=List[str])
def list_models():
    return settings.verification_models

@router.post("/verify", response_model=VerifyResponse)
async def verify_multipart(
    image1: UploadFile = File(..., description="First image (jpeg/png)"),
    image2: UploadFile = File(..., description="Second image (jpeg/png)")
):
    img1 = read_image(image1)
    img2 = read_image(image2)
    result = verify_pair(img1, img2, settings.verification_models)
    return VerifyResponse(**result)

@router.post("/verify-b64", response_model=VerifyResponse)
async def verify_base64(payload: VerifyB64Request):
    img1 = read_image_b64(payload.image1_b64)
    img2 = read_image_b64(payload.image2_b64)
    result = verify_pair(img1, img2, settings.verification_models)
    return VerifyResponse(**result)

@router.get("/healthz")
def healthz():
    return {"status": "ok", "app": settings.app_name, "version": settings.version}
