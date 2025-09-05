from functools import lru_cache
from deepface import DeepFace

@lru_cache(maxsize=16)
def get_model(model_name: str):
    # DeepFace caches internally too; this ensures single init per process
    return DeepFace.build_model(model_name)