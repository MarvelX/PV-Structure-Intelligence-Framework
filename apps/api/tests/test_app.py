from __future__ import annotations

import time
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from api.config import get_settings
from api.main import create_app


ROOT_DIR = Path(__file__).resolve().parents[3]
ASSETS_DIR = ROOT_DIR / "data" / "assets"


@pytest.fixture()
async def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> AsyncClient:
    runtime_dir = tmp_path / "runtime"
    exports_dir = runtime_dir / "exports"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    exports_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("WORKING_TOOL_ASSETS_DIR", str(ASSETS_DIR))
    monkeypatch.setenv("WORKING_TOOL_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("WORKING_TOOL_EXPORTS_DIR", str(exports_dir))
    monkeypatch.setenv("WORKING_TOOL_SQLITE_BUSY_RETRIES", "2")

    get_settings.cache_clear()
    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as async_client:
        yield async_client


@pytest.mark.asyncio()
async def test_home_recent_records_defaults_to_six(client: AsyncClient) -> None:
    response = await client.get("/api/home/recent-records")

    assert response.status_code == 200
    assert response.json() == {"items": []}


@pytest.mark.asyncio()
async def test_waterbase_evaluate_returns_ready_for_exact_rule_match(client: AsyncClient) -> None:
    response = await client.post(
        "/api/workspaces/waterbase/evaluate",
        json={
            "structure_type": "clear_water_tank",
            "is_retrofit": "yes",
            "span_level": "high",
            "wind_level": "high",
            "corrosion_level": "high",
            "interference_level": "high",
            "om_requirement": "high",
            "support_condition": "outer_support_only",
            "target_market": "CN",
            "engineering_inputs": {"wind_speed_m_s": 42},
            "constraint_notes": "Need fast pre-check",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["state"] == "ready"
    assert payload["title_zh"].startswith("WaterBase")
    assert payload["workspace_specific_result"]["recommended_path"] == "优先评估柔性支架路径"
    assert payload["linked_asset_refs"]["rule_ids"] == ["WB-001"]
    assert payload["linked_asset_refs"]["case_ids"] == ["case_nanchang_water_plant"]
    assert "WaterBase Mount" in payload["export_text"]


@pytest.mark.asyncio()
async def test_overseas_evaluate_returns_manual_override_when_rule_not_confident(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/workspaces/overseas/evaluate",
        json={
            "project_type": "carport_walkway",
            "structure_scenario": "complex_existing_structure",
            "load_environment": "snow",
            "foundation_condition": "restricted_foundation",
            "site_constraint": "normal_window",
            "target_market": "EU",
            "engineering_inputs": {"snow_load_kpa": 1.8},
            "compliance_notes": "Need EU file package",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["state"] == "manual_override"
    assert payload["workspace_specific_result"]["review_conclusion"] == "进入专项技术评审"
    assert payload["linked_asset_refs"]["rule_ids"] == []
    assert payload["linked_asset_refs"]["gate_ids"] == ["project_lifecycle_control_gates"]
    assert payload["linked_asset_refs"]["checklist_ids"] == ["design_institute_audit_checklist"]


@pytest.mark.asyncio()
async def test_create_record_rejects_pending_state(client: AsyncClient) -> None:
    response = await client.post(
        "/api/records",
        json={
            "workspace": "waterbase",
            "title_zh": "Pending Draft",
            "title_en": "Pending Draft",
            "status": "pending",
            "summary": "Should not save while pending",
            "tags": ["invalid"],
            "manual_override": None,
            "input": {"structure_type": "clear_water_tank"},
            "output": {"recommended_path": "优先评估柔性支架路径"},
            "exports": {
                "markdown": "# Pending Draft",
                "text": "Pending Draft",
            },
            "links": {
                "rule_ids": ["WB-001"],
                "case_ids": ["case_nanchang_water_plant"],
            },
        },
    )

    assert response.status_code == 422
    assert "pending" in response.text


@pytest.mark.asyncio()
async def test_create_record_persists_record_and_surfaces_in_recent_and_detail(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/records",
        json={
            "workspace": "overseas",
            "title_zh": "日本既有屋面抗震评审",
            "title_en": "JP Retrofit Roof Seismic Review",
            "status": "manual_override",
            "summary": "Need manual conclusion before final sign-off.",
            "tags": ["JP", "retrofit"],
            "manual_override": {
                "conclusion": "人工复核后建议专项评审",
                "note": "Need local institute confirmation",
            },
            "input": {
                "project_type": "retrofit_roof",
                "structure_scenario": "concrete_roof",
            },
            "output": {
                "review_conclusion": "进入专项技术评审",
                "review_signal": "重点关注既有结构承载和抗震细部做法",
            },
            "exports": {
                "markdown": "# JP Retrofit Roof Seismic Review",
                "text": "JP Retrofit Roof Seismic Review",
            },
            "links": {
                "rule_ids": ["TR-003"],
                "gate_ids": ["project_lifecycle_control_gates"],
                "checklist_ids": ["design_institute_audit_checklist"],
            },
        },
    )

    assert create_response.status_code == 201
    record_id = create_response.json()["id"]

    detail_response = await client.get(f"/api/records/{record_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["title_zh"] == "日本既有屋面抗震评审"
    assert detail["manual_override"]["conclusion"] == "人工复核后建议专项评审"

    recent_response = await client.get("/api/home/recent-records?limit=6")
    assert recent_response.status_code == 200
    recent_items = recent_response.json()["items"]
    assert len(recent_items) == 1
    assert recent_items[0]["id"] == record_id
    assert recent_items[0]["workspace"] == "overseas"


@pytest.mark.asyncio()
async def test_evaluate_returns_504_when_backend_exceeds_timeout(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_dir = tmp_path / "runtime"
    exports_dir = runtime_dir / "exports"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    exports_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("WORKING_TOOL_ASSETS_DIR", str(ASSETS_DIR))
    monkeypatch.setenv("WORKING_TOOL_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("WORKING_TOOL_EXPORTS_DIR", str(exports_dir))
    monkeypatch.setenv("WORKING_TOOL_EVALUATE_TIMEOUT_SECONDS", "0.01")

    get_settings.cache_clear()
    app = create_app()

    def slow_evaluate(_payload):
        time.sleep(0.05)
        return None

    app.state.evaluator.evaluate_waterbase = slow_evaluate

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as async_client:
        response = await async_client.post(
            "/api/workspaces/waterbase/evaluate",
            json={
                "structure_type": "clear_water_tank",
                "is_retrofit": "yes",
                "span_level": "high",
                "wind_level": "high",
                "corrosion_level": "high",
                "interference_level": "high",
                "om_requirement": "high",
                "support_condition": "outer_support_only",
                "target_market": "CN",
                "engineering_inputs": {},
                "constraint_notes": "slow path",
            },
        )

    assert response.status_code == 504
    assert "timed out" in response.text.lower()
