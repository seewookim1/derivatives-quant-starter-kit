"""환경변수 기반 설정 - pydantic Settings"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://hdesk:hdesk_secret@localhost:5432/hdesk_db"
    )
    database_url_sync: str = Field(
        default="postgresql+psycopg2://hdesk:hdesk_secret@localhost:5432/hdesk_db"
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_debug: bool = Field(default=False)

    # Dashboard
    dash_host: str = Field(default="0.0.0.0")
    dash_port: int = Field(default=8050)

    # Risk Parameters
    default_risk_free_rate: float = Field(default=0.035)
    default_var_confidence: float = Field(default=0.99)
    default_var_lookback_days: int = Field(default=252)
    risk_limit_net_delta: float = Field(default=1000.0)
    risk_limit_net_vega: float = Field(default=500_000.0)

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
