"""
Application settings — loaded once from .env via pydantic-settings.
Import get_settings() anywhere to access config values.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# speechfix/ root (two levels up from core/config.py)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "SpeechFix"
    DEBUG: bool = False

    # AI keys
    GEMINI_API_KEY: str

    # Faster-Whisper
    WHISPER_MODEL_SIZE: str = "small"
    WHISPER_DEVICE: str = "cpu"

    WHISPER_COMPUTE_TYPE: str = "int8"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    lru_cache ensures .env is read only once at startup.
    """
    return Settings()
