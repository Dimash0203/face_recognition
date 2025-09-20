# app/weights_sync.py
from __future__ import annotations
import os, shutil
from pathlib import Path
from .config import settings

def ensure_local_weights_available() -> Path:
    # Направляем DeepFace кешироваться в корень проекта
    os.environ["DEEPFACE_HOME"] = str(settings.deepface_home)

    deepface_cache = settings.deepface_home / ".deepface" / "weights"
    deepface_cache.mkdir(parents=True, exist_ok=True)

    if not settings.weights_dir.exists():
        raise RuntimeError(f"Каталог с весами не найден: {settings.weights_dir}")

    # Копируем *.h5 (Facenet/Retinaface)
    for src in settings.weights_dir.glob("*.h5"):
        dst = deepface_cache / src.name
        if (not dst.exists()) or (dst.stat().st_size != src.stat().st_size):
            shutil.copy2(src, dst)

    return deepface_cache
