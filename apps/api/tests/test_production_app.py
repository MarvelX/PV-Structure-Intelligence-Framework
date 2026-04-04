from __future__ import annotations

from pathlib import Path
import importlib
import sys
import types

import pytest
from httpx import ASGITransport, AsyncClient


ROOT_DIR = Path(__file__).resolve().parents[3]
ASSETS_DIR = ROOT_DIR / "data" / "assets"
API_SRC_DIR = ROOT_DIR / "apps" / "api" / "src" / "api"


def _build_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, include_assets: bool = True, include_index: bool = True):
    runtime_dir = tmp_path / "runtime"
    exports_dir = runtime_dir / "exports"
    dist_dir = tmp_path / "dist"

    monkeypatch.setenv("WORKING_TOOL_ASSETS_DIR", str(ASSETS_DIR))
    monkeypatch.setenv("WORKING_TOOL_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("WORKING_TOOL_EXPORTS_DIR", str(exports_dir))
    monkeypatch.setenv("WORKING_TOOL_WEB_DIST_DIR", str(dist_dir))

    runtime_dir.mkdir(parents=True, exist_ok=True)
    exports_dir.mkdir(parents=True, exist_ok=True)
    if include_assets:
        (dist_dir / "assets").mkdir(parents=True, exist_ok=True)
    if include_index:
        dist_dir.mkdir(parents=True, exist_ok=True)
        (dist_dir / "index.html").write_text("<html><body>prod app</body></html>", encoding="utf-8")

    api_package = sys.modules.get("api")
    if api_package is None:
        api_package = types.ModuleType("api")
        api_package.__path__ = [str(API_SRC_DIR)]
        sys.modules["api"] = api_package

    config_module = importlib.import_module("api.config")
    config_module.get_settings.cache_clear()

    main_module = importlib.import_module("api.main")
    main_module = importlib.reload(main_module)
    return main_module.app


@pytest.mark.asyncio()
async def test_root_route_serves_built_index_html(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(tmp_path, monkeypatch)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.text == "<html><body>prod app</body></html>"


@pytest.mark.asyncio()
async def test_spa_route_falls_back_to_index_html(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(tmp_path, monkeypatch)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/records/abc123")

    assert response.status_code == 200
    assert response.text == "<html><body>prod app</body></html>"


@pytest.mark.asyncio()
async def test_missing_assets_dir_does_not_break_root_serving(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _build_app(tmp_path, monkeypatch, include_assets=False)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert response.text == "<html><body>prod app</body></html>"


@pytest.mark.asyncio()
async def test_missing_index_html_keeps_root_route_unregistered(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _build_app(tmp_path, monkeypatch, include_index=False)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/")

    assert response.status_code == 404


@pytest.mark.asyncio()
async def test_missing_api_path_is_not_swallowed_by_spa_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = _build_app(tmp_path, monkeypatch)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/api/does-not-exist")

    assert response.status_code == 404
