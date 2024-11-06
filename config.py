from pydantic import BaseSettings, validator
from pathlib import Path


class Settings(BaseSettings):
    MODELS_DIR: Path

    PORT: int
    MAX_WORKERS: int

    CACHE_TTL: int

    METRICS_PORT: int

    LOG_LEVEL: str
    MODEL_VERSION: str


    @validator('MODELS_DIR')
    def validate_models_dir(cls, v):
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Directory {path} does not exist")
        return path

    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v.upper()

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True


settings = Settings()
