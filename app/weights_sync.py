from __future__ import annotations
import os, shutil
from pathlib import Path
from .config import settings

def ensure_local_weights_available() -> Path:
    os.environ["DEEPFACE_HOME"] = str(settings.deepface_home)  # e.g., project root

    deepface_cache = settings.deepface_home / ".deepface" / "weights"
    deepface_cache.mkdir(parents=True, exist_ok=True)

    if not settings.weights_dir.exists():
        raise RuntimeError(f"Weights dir not found: {settings.weights_dir}")

    # copy .h5 files if missing / changed size
    for src in settings.weights_dir.glob("*.h5"):
        dst = deepface_cache / src.name
        try:
            if (not dst.exists()) or (dst.stat().st_size != src.stat().st_size):
                shutil.copy2(src, dst)
        except Exception as e:
            raise RuntimeError(f"Failed to copy weight {src} -> {dst}: {e}")

    return deepface_cache
