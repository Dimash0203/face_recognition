# main.py
import contextlib
import os
import warnings
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.api import router
from app.utils.config import settings
from app.models.weights_sync import ensure_local_weights_available
from app.models.models_registry import get_model
from app.utils.logger import setup_logging
from app.utils.watchdog import watchdog_task

# Подавление "шумных" сообщений
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
warnings.filterwarnings("ignore", category=UserWarning, module="tf_keras")

logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1) Готовим веса
    cache_path = ensure_local_weights_available()
    logger.info("[startup] Весовые файлы доступны в: {}", cache_path)

    # 2) Прогреваем Facenet
    for name in settings.verification_models:
        try:
            get_model(name)
            logger.info("[startup] Модель '{}' загружена", name)
        except Exception as e:
            logger.exception("[startup] Не удалось загрузить модель '{}': {}", name, e)

    # 3) Watchdog
    task = None
    if settings.watchdog_enabled:
        task = asyncio.create_task(watchdog_task())
        logger.info("[startup] Watchdog запущен (interval={}s)", settings.watchdog_interval_sec)

    try:
        yield
    finally:
        if task:
            task.cancel()
            with contextlib.suppress(Exception):
                await task
        logger.info("[shutdown] Завершение работы приложения")

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
