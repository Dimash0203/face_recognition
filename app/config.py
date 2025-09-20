# app/config.py
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Базовая информация
    app_name: str = "Face Verification API"
    version: str = "1.2.0"

    # Важно:
    # - env_file: читаем .env в корне проекта
    # - case_sensitive=False: ключи переменных окружения и .env НЕчувствительны к регистру
    #   => WATCHDOG_INTERVAL_SEC и watchdog_interval_sec эквивалентны
    # - env_prefix="": не добавляем префиксы к именам переменных
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix=""
    )

    # Пути проекта
    project_root: Path = Path(__file__).resolve().parents[1]
    weights_dir: Path = project_root / "weights"
    deepface_home: Path = project_root  # DeepFace создаст .deepface внутри

    # Только Facenet
    verification_models: list[str] = Field(default=["Facenet"])

    # Детекторы
    primary_detector: str = "opencv"
    fallback_detector: str = "retinaface"  # используется только если есть локальный .h5

    # Порог по умолчанию
    threshold: float = 0.70

    # Лимит размера входного файла
    max_image_bytes: int = 5 * 1024 * 1024  # 5 MB

    # Логи
    log_dir: Path = project_root / "logs"
    log_level: str = "INFO"
    log_rotation: str = "10 MB"
    log_retention: str = "7 days"
    log_filename: str = "app.txt"

    # Watchdog / авто-санация
    watchdog_enabled: bool = True
    watchdog_interval_sec: int = 600
    smoketest_image_path: Optional[Path] = None  # строка из .env будет преобразована в Path

settings = Settings()
