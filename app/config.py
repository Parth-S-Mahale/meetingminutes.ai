from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # App Settings
    APP_NAME: str = "Meeting Summarizer API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./meeting_summarizer.db"

    # File Storage
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    MAX_FILE_SIZE_MB: int = 100
    ALLOWED_AUDIO_EXTENSIONS: List[str] = [".mp3", ".wav", ".m4a", ".aac", ".mp4"]

    # Hugging Face / Models
    HF_TOKEN: str = ""

    # ASR / Whisper
    ASR_MODEL_ID: str = "openai/whisper-medium.en"
    ASR_DEVICE: str = "cpu"
    ASR_DTYPE: str = "float32"
    ASR_CHUNK_LENGTH_S: int = 30

    # Summarizer LLM
    SUMMARIZER_MODEL_ID: str = "meta-llama/Llama-3.2-3B-Instruct"
    SUMMARIZER_DEVICE_MAP: str = "auto"
    SUMMARIZER_LOAD_IN_4BIT: bool = True
    MAX_NEW_TOKENS: int = 800
    TEMPERATURE: float = 0.2
    TOP_P: float = 0.9

    # Optional fallback provider
    OPENAI_API_KEY: str = ""

    @field_validator("ALLOWED_AUDIO_EXTENSIONS", mode="before")
    @classmethod
    def parse_audio_extensions(cls, value):
        if isinstance(value, str):
            return [ext.strip() for ext in value.split(",") if ext.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()