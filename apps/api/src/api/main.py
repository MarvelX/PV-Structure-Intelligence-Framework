from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query

from .assets import load_catalog
from .config import Settings, get_settings
from .evaluator import Evaluator
from .schemas import (
    EvaluateResponse,
    OverseasEvaluateRequest,
    RecentRecordsResponse,
    RecordCreateRequest,
    RecordResponse,
    WaterbaseEvaluateRequest,
)
from .storage import ExportService, RecordRepository


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    resolved_settings.runtime_dir.mkdir(parents=True, exist_ok=True)
    resolved_settings.exports_dir.mkdir(parents=True, exist_ok=True)

    repository = RecordRepository(
        database_path=resolved_settings.database_path,
        busy_retries=resolved_settings.sqlite_busy_retries,
    )
    repository.initialize()

    app = FastAPI(title="V1 Working Tool API")
    app.state.evaluator = Evaluator(load_catalog(resolved_settings.assets_dir))
    app.state.repository = repository
    app.state.export_service = ExportService(resolved_settings.exports_dir)

    @app.get("/api/home/recent-records", response_model=RecentRecordsResponse)
    async def list_recent_records(limit: int = Query(default=6, ge=1, le=20)) -> RecentRecordsResponse:
        items = app.state.repository.list_recent_records(limit=limit)
        return RecentRecordsResponse(items=items)

    @app.post("/api/workspaces/waterbase/evaluate", response_model=EvaluateResponse)
    async def evaluate_waterbase(payload: WaterbaseEvaluateRequest) -> EvaluateResponse:
        try:
            return app.state.evaluator.evaluate_waterbase(payload)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/workspaces/overseas/evaluate", response_model=EvaluateResponse)
    async def evaluate_overseas(payload: OverseasEvaluateRequest) -> EvaluateResponse:
        try:
            return app.state.evaluator.evaluate_overseas(payload)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/records", response_model=RecordResponse, status_code=201)
    async def create_record(payload: RecordCreateRequest) -> RecordResponse:
        return app.state.repository.create_record(payload, app.state.export_service)

    @app.get("/api/records/{record_id}", response_model=RecordResponse)
    async def get_record(record_id: str) -> RecordResponse:
        try:
            return app.state.repository.get_record(record_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Record {record_id} not found") from exc

    return app


app = create_app()


def main() -> Any:
    return app
