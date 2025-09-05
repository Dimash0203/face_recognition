# app/config.py
from pathlib import Path
from typing import List
import re
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

SUPPORTED_MODELS = ["Facenet", "Facenet512", "ArcFace", "VGG-Face"]

def read_models_txt(path: Path, default: List[str]) -> List[str]:
    if not path.exists():
        return default

    enabled: List[str] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9\-]+)\s*=\s*(true|false)$", line, flags=re.I)
        if not m:
            # silently skip malformed lines
            continue
        name, flag = m.group(1), m.group(2).lower() == "true"
        if name not in SUPPORTED_MODELS:
            # unknown model -> skip
            continue
        if flag:
            enabled.append(name)

    return enabled or default

class Settings(BaseSettings):
    app_name: str = "Face Verification API"
    version: str = "1.0.0"

    # load from .env if present
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Project paths
    project_root: Path = Path(__file__).resolve().parents[1]
    weights_dir: Path = project_root / "weights"
    deepface_home: Path = project_root

    # models.txt location
    models_txt_path: Path = project_root / "models.txt"

    # Default models if models.txt is missing/empty (keep your original default)
    verification_models: list[str] = Field(default=["Facenet"])  # :contentReference[oaicite:1]{index=1}

    # Detector preference
    primary_detector: str = "retinaface"
    fallback_detector: str = "yunet"

    # Decision/score
    threshold: float = 0.70
    percent_low: float = 0.30
    percent_high: float = 0.95

    # Upload limits
    max_image_bytes: int = 5 * 1024 * 1024  # 5 MB

    @property
    def selected_models(self) -> list[str]:
        return read_models_txt(self.models_txt_path, self.verification_models)

settings = Settings()
