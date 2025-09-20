# app/logger.py
import logging
import sys
from pathlib import Path
from loguru import logger
from .config import settings

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except Exception:
            level = record.levelno
        logger.bind(logger_name=record.name).opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

def setup_logging():
    # Папка для логов
    Path(settings.log_dir).mkdir(parents=True, exist_ok=True)
    log_path = Path(settings.log_dir) / settings.log_filename

    # Чистим старые хендлеры
    logger.remove()

    # Консоль (кратко)
    logger.add(
        sys.stderr,
        level=settings.log_level,
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {message}"
    )

    # Файл (ротация/ретеншн)
    logger.add(
        log_path,
        level=settings.log_level,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        encoding="utf-8",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}"
    )

    # Перехватываем стандартный logging (uvicorn / fastapi)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).setLevel(logging.INFO)

    logger.info("Логирование настроено. Файл: {}", log_path)
    return logger
