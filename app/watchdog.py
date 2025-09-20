# app/watchdog.py
import asyncio
from typing import Optional
import cv2
import numpy as np
from loguru import logger
from .config import settings
from .service import verify_pair
from .models_registry import reset_models

def _make_dummy_pair() -> Optional[tuple[np.ndarray, np.ndarray]]:
    """
    Пытаемся загрузить smoketest_image_path, если задан.
    Если не задан — возвращаем None (watchdog будет «молчаливым»).
    """
    path = settings.smoketest_image_path
    if not path:
        return None
    img = cv2.imread(str(path))
    if img is None:
        logger.warning("[watchdog] Не удалось прочитать smoketest_image_path: {}", path)
        return None
    return img, img  # сравним само с собой

async def watchdog_task():
    if not settings.watchdog_enabled:
        return
    pair = _make_dummy_pair()
    if pair is None:
        logger.info("[watchdog] smoketest отключён (нет изображения). Буду спать, но контроль не выполняю.")
        return

    img1, img2 = pair
    while True:
        try:
            # Используем дефолтный порог; модель одна — Facenet
            res = verify_pair(img1, img2, settings.verification_models, settings.threshold)
            # Если внутри «внутренняя ошибка» — verify_pair уже сам делал reset+retry
            ok = all("error" not in r for r in res["results"])
            if ok:
                logger.debug("[watchdog] ok")
            else:
                logger.warning("[watchdog] Обнаружены ошибки в смоук-тесте: {}", res["results"])
        except Exception as e:
            # жёсткий случай — пытаемся принудительно восстановиться
            logger.exception("[watchdog] Исключение во время смоук-теста: {}", e)
            reset_models()
        await asyncio.sleep(settings.watchdog_interval_sec)
