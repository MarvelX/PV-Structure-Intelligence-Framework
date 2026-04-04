from __future__ import annotations

from pathlib import Path
import sys

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

from .config import Settings, get_settings


BASELINE_REVISION = "0001_create_records_table"


def resolve_bundle_root() -> Path:
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root)
    return Path(__file__).resolve().parents[2]


def build_alembic_config(bundle_root: Path, database_path: Path) -> Config:
    config = Config(str(bundle_root / "alembic.ini"))
    config.set_main_option("script_location", str(bundle_root / "alembic"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")
    return config


def upgrade_database(settings: Settings | None = None, *, bundle_root: Path | None = None) -> None:
    resolved_settings = settings or get_settings()
    resolved_settings.runtime_dir.mkdir(parents=True, exist_ok=True)

    resolved_bundle_root = bundle_root or resolve_bundle_root()
    config = build_alembic_config(resolved_bundle_root, resolved_settings.database_path)

    current_head = ScriptDirectory.from_config(config).get_current_head()
    engine = create_engine(f"sqlite:///{resolved_settings.database_path}")
    adopted_legacy_schema = False
    with engine.begin() as connection:
        tables = set(inspect(connection).get_table_names())
        if "records" in tables and "alembic_version" not in tables:
            connection.execute(
                text(
                    "CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)"
                )
            )
            connection.execute(
                text("INSERT INTO alembic_version (version_num) VALUES (:revision)"),
                {"revision": BASELINE_REVISION},
            )
            adopted_legacy_schema = True

    if adopted_legacy_schema and current_head == BASELINE_REVISION:
        return

    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")


def main() -> None:
    upgrade_database()


if __name__ == "__main__":
    main()
