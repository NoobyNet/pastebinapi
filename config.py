from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PASTEBIN_BASE_URL: str
    DEV_API_KEY: str
    USER_NAME: str
    USER_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached instance of the settings.
    lru_cache ensures we only read the environment variables once.
    Can be used as a FastAPI dependency.
    """
    return Settings()


# Singleton instance for backward compatibility
settings = get_settings()
