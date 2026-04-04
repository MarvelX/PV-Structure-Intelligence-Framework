from __future__ import annotations

import json
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import DateTime, String, Text, create_engine, desc, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .schemas import ExportPayload, LinkedAssetRefs, ManualOverridePayload, RecordCreateRequest, RecordResponse


class Base(DeclarativeBase):
    pass


class RecordEntity(Base):
    __tablename__ = "records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workspace: Mapped[str] = mapped_column(String(32), index=True)
    title_zh: Mapped[str] = mapped_column(String(255))
    title_en: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(32), index=True)
    tags: Mapped[str] = mapped_column(Text, default="[]")
    summary: Mapped[str] = mapped_column(Text)
    manual_override: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    input_json: Mapped[str] = mapped_column(Text)
    output_json: Mapped[str] = mapped_column(Text)
    exports_json: Mapped[str] = mapped_column(Text)
    links_json: Mapped[str] = mapped_column(Text)


@dataclass
class ExportService:
    exports_dir: Path

    def write(self, workspace: str, record_id: str, title_en: str, markdown: str, text: str) -> tuple[List[str], List[str]]:
        safe_name = title_en.lower().replace(" ", "-")[:80] or record_id
        target_dir = self.exports_dir / workspace
        target_dir.mkdir(parents=True, exist_ok=True)
        files: List[str] = []
        errors: List[str] = []

        for suffix, content in (("md", markdown), ("txt", text)):
            destination = target_dir / f"{safe_name}-{record_id}.{suffix}"
            try:
                _atomic_write(destination, content)
                files.append(str(destination))
            except OSError as exc:
                errors.append(f"{suffix} export failed: {exc}")

        return files, errors


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(content)
        temp_path = Path(handle.name)
    temp_path.replace(path)


class RecordRepository:
    def __init__(self, database_path: Path, busy_retries: int = 3) -> None:
        self._busy_retries = busy_retries
        self._database_path = database_path
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._engine = create_engine(
            f"sqlite:///{self._database_path}",
            connect_args={"check_same_thread": False},
        )
        self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)

    def initialize(self) -> None:
        Base.metadata.create_all(self._engine)

    def create_record(self, payload: RecordCreateRequest, export_service: ExportService) -> RecordResponse:
        record_id = uuid4().hex
        now = datetime.now(timezone.utc)
        files, errors = export_service.write(
            workspace=payload.workspace,
            record_id=record_id,
            title_en=payload.title_en,
            markdown=payload.exports.markdown,
            text=payload.exports.text,
        )
        exports = payload.exports.model_copy(update={"files": files, "errors": errors})

        entity = RecordEntity(
            id=record_id,
            workspace=payload.workspace,
            title_zh=payload.title_zh,
            title_en=payload.title_en,
            status=payload.status,
            tags=json.dumps(payload.tags, ensure_ascii=False),
            summary=payload.summary,
            manual_override=_dumps(payload.manual_override.model_dump()) if payload.manual_override else None,
            created_at=now,
            updated_at=now,
            input_json=_dumps(payload.input),
            output_json=_dumps(payload.output),
            exports_json=_dumps(exports.model_dump()),
            links_json=_dumps(payload.links.model_dump()),
        )

        def _save(session: Session) -> None:
            session.add(entity)
            session.commit()

        self._with_retry(_save)
        return self.get_record(record_id)

    def get_record(self, record_id: str) -> RecordResponse:
        with self._session_factory() as session:
            entity = session.get(RecordEntity, record_id)
            if entity is None:
                raise KeyError(record_id)
            return _to_record_response(entity)

    def list_recent_records(self, limit: int = 6) -> List[RecordResponse]:
        with self._session_factory() as session:
            statement = select(RecordEntity).order_by(desc(RecordEntity.updated_at)).limit(limit)
            entities = session.execute(statement).scalars().all()
            return [_to_record_response(entity) for entity in entities]

    def _with_retry(self, action) -> None:
        for attempt in range(self._busy_retries + 1):
            try:
                with self._session_factory() as session:
                    action(session)
                return
            except OperationalError as exc:
                if "locked" not in str(exc).lower() or attempt >= self._busy_retries:
                    raise
                time.sleep(0.05 * (attempt + 1))


def _to_record_response(entity: RecordEntity) -> RecordResponse:
    return RecordResponse(
        id=entity.id,
        workspace=entity.workspace,
        title_zh=entity.title_zh,
        title_en=entity.title_en,
        status=entity.status,
        tags=json.loads(entity.tags),
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        summary=entity.summary,
        manual_override=ManualOverridePayload(**json.loads(entity.manual_override)) if entity.manual_override else None,
        input=json.loads(entity.input_json),
        output=json.loads(entity.output_json),
        exports=ExportPayload(**json.loads(entity.exports_json)),
        links=LinkedAssetRefs(**json.loads(entity.links_json)),
    )


def _dumps(value: Dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False)
