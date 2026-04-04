from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, inspect, text

from api.config import Settings
from api.migrations import BASELINE_REVISION, upgrade_database
from api.storage import RecordRepository


def test_upgrade_database_stamps_legacy_sqlite_schema(tmp_path: Path) -> None:
    runtime_dir = tmp_path / "runtime"
    exports_dir = runtime_dir / "exports"
    assets_dir = tmp_path / "assets"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    exports_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    settings = Settings(
        assets_dir=assets_dir,
        runtime_dir=runtime_dir,
        exports_dir=exports_dir,
        sqlite_busy_retries=2,
    )

    repository = RecordRepository(database_path=settings.database_path, busy_retries=2)
    repository.initialize()

    upgrade_database(settings)

    engine = create_engine(f"sqlite:///{settings.database_path}")
    with engine.connect() as connection:
        tables = set(inspect(connection).get_table_names())
        assert "records" in tables
        assert "alembic_version" in tables
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()

    assert revision == BASELINE_REVISION
