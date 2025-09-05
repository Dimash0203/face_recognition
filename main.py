# main.py
import os
from app.api import router
from app.config import settings
from app.weights_sync import ensure_local_weights_available
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.models_registry import get_model
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure DeepFace loads weights from project ./weights
    cache_path = ensure_local_weights_available()
    print(f"[startup] Weights available at: {cache_path}")
    # preload models
    for name in settings.verification_models:
        get_model(name)

    yield

app = FastAPI(title=settings.app_name, version=settings.version, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST","GET","OPTIONS"],
    allow_headers=["*"],
)
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=2)
