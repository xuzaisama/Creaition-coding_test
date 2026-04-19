from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables once at startup."""

    app_name: str = os.getenv("APP_NAME", "Intelligent Task Management System")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./task_manager.db")
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "60"))


settings = Settings()
