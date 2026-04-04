from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="WORKING_TOOL_",
        extra="ignore",
    )

    assets_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[4] / "data" / "assets")
    runtime_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[4] / "data" / "runtime")
    exports_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[4] / "data" / "runtime" / "exports")
    sqlite_busy_retries: int = 3
    evaluate_timeout_seconds: float = 10.0

    @property
    def database_path(self) -> Path:
        return self.runtime_dir / "working_tool.sqlite3"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
