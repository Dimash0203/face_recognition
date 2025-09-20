# app/models_registry.py
from deepface import DeepFace
from typing import Dict
from loguru import logger

# Простой словарный кэш вместо lru_cache, чтобы можно было «жёстко» очищать
_MODEL_CACHE: Dict[str, object] = {}

def get_model(model_name: str):
    m = _MODEL_CACHE.get(model_name)
    if m is None:
        logger.info("Загрузка модели '{}'", model_name)
        m = DeepFace.build_model(model_name)
        _MODEL_CACHE[model_name] = m
    return m

def reset_models():
    """
    Полностью очистить сессию TF/Keras и локальный кэш моделей.
    Помогает вылечить зависшие графы/сессии после редких исключений.
    """
    try:
        import tf_keras as keras  # соответствует TF 2.17
        keras.backend.clear_session()
        logger.info("tf_keras.backend.clear_session() выполнен")
    except Exception as e:
        logger.warning("Не удалось очистить Keras session: {}", e)
    _MODEL_CACHE.clear()
    logger.info("Кэш моделей очищен")
