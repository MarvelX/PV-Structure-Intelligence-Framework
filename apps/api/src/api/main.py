from __future__ import annotations

import asyncio
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
    RecordUpdateRequest,
    WaterbaseEvaluateRequest,
)
from .storage import ExportService, RecordConflictError, RecordRepository


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
            return await asyncio.wait_for(
                asyncio.to_thread(app.state.evaluator.evaluate_waterbase, payload),
                timeout=resolved_settings.evaluate_timeout_seconds,
            )
        except asyncio.TimeoutError as exc:
            raise HTTPException(
                status_code=504,
                detail=f"Evaluation timed out after {resolved_settings.evaluate_timeout_seconds:g} seconds",
            ) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/workspaces/overseas/evaluate", response_model=EvaluateResponse)
    async def evaluate_overseas(payload: OverseasEvaluateRequest) -> EvaluateResponse:
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(app.state.evaluator.evaluate_overseas, payload),
                timeout=resolved_settings.evaluate_timeout_seconds,
            )
        except asyncio.TimeoutError as exc:
            raise HTTPException(
                status_code=504,
                detail=f"Evaluation timed out after {resolved_settings.evaluate_timeout_seconds:g} seconds",
            ) from exc
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

    @app.patch("/api/records/{record_id}", response_model=RecordResponse)
    async def update_record(record_id: str, payload: RecordUpdateRequest) -> RecordResponse:
        try:
            return app.state.repository.update_record(record_id, payload, app.state.export_service)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Record {record_id} not found") from exc
        except RecordConflictError as exc:
            raise HTTPException(
                status_code=409,
                detail=f"Record {record_id} was updated by another session. Refresh and retry.",
            ) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return app


app = create_app()


def main() -> Any:
    return app
