# macOS Local Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a macOS double-clickable `.app` for V1 Working Tool by converting the app to a single production FastAPI service, adding a Python launcher, and packaging it with PyInstaller.

**Architecture:** The web frontend is built to static assets and served by FastAPI in production mode. A Python launcher becomes the only entrypoint: it resolves packaged resources via absolute paths, runs migrations, finds a free local port, starts the API, opens the browser, and cleans up child processes on exit.

**Tech Stack:** FastAPI, Starlette static files, React/Vite build output, Alembic, PyInstaller, Python `subprocess`/`signal`/`socket`, shell packaging scripts.

---

### Task 1: Serve Built Frontend From FastAPI

**Files:**
- Create: `apps/api/tests/test_production_app.py`
- Modify: `apps/api/src/api/config.py`
- Modify: `apps/api/src/api/main.py`
- Test: `apps/api/tests/test_production_app.py`

- [ ] **Step 1: Write the failing production app tests**

```python
from pathlib import Path

from httpx import ASGITransport, AsyncClient

from api.main import create_app
from api.config import Settings


async def test_root_route_serves_built_index(tmp_path: Path):
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    (dist_dir / "index.html").write_text("<html><body>prod app</body></html>", encoding="utf-8")

    settings = Settings(web_dist_dir=dist_dir)
    app = create_app(settings)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert "prod app" in response.text


async def test_non_api_route_falls_back_to_index_html(tmp_path: Path):
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    (dist_dir / "index.html").write_text("<html><body>spa fallback</body></html>", encoding="utf-8")

    settings = Settings(web_dist_dir=dist_dir)
    app = create_app(settings)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/records/abc123")

    assert response.status_code == 200
    assert "spa fallback" in response.text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/api && uv run pytest tests/test_production_app.py -v`  
Expected: FAIL because FastAPI currently does not mount the built frontend or SPA fallback route.

- [ ] **Step 3: Write the minimal production serving implementation**

```python
# apps/api/src/api/config.py
class Settings(BaseSettings):
    ...
    web_dist_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[4] / "apps" / "web" / "dist"
    )


# apps/api/src/api/main.py
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

...
if resolved_settings.web_dist_dir.exists():
    app.mount("/assets", StaticFiles(directory=resolved_settings.web_dist_dir / "assets"), name="web-assets")

    @app.get("/")
    async def serve_index() -> FileResponse:
        return FileResponse(resolved_settings.web_dist_dir / "index.html")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(resolved_settings.web_dist_dir / "index.html")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd apps/api && uv run pytest tests/test_production_app.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/api/src/api/config.py apps/api/src/api/main.py apps/api/tests/test_production_app.py
git commit -m "feat: serve built frontend from fastapi"
```

### Task 2: Add Launcher With Absolute Resource Paths, Dynamic Port, And Signal Cleanup

**Files:**
- Create: `apps/api/src/api/launcher.py`
- Create: `apps/api/tests/test_launcher.py`
- Modify: `apps/api/src/api/migrations.py`
- Modify: `apps/api/src/api/config.py`
- Test: `apps/api/tests/test_launcher.py`

- [ ] **Step 1: Write the failing launcher tests**

```python
from pathlib import Path

from api.launcher import resolve_bundle_root, reserve_free_port


def test_resolve_bundle_root_prefers_meipass(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("sys._MEIPASS", str(tmp_path), raising=False)
    assert resolve_bundle_root() == tmp_path


def test_reserve_free_port_returns_positive_port():
    port = reserve_free_port()
    assert isinstance(port, int)
    assert port > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/api && uv run pytest tests/test_launcher.py -v`  
Expected: FAIL because the launcher module does not exist yet.

- [ ] **Step 3: Implement launcher foundations**

```python
# apps/api/src/api/launcher.py
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path


def resolve_bundle_root() -> Path:
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    return Path(__file__).resolve().parents[2]


def reserve_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def install_signal_handlers(cleanup):
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
```

```python
# apps/api/src/api/migrations.py
def build_alembic_config(bundle_root: Path, database_path: Path) -> Config:
    config = Config(str(bundle_root / "alembic.ini"))
    config.set_main_option("script_location", str(bundle_root / "alembic"))
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")
    return config
```

- [ ] **Step 4: Expand launcher to start the server and open the browser**

```python
def main() -> None:
    bundle_root = resolve_bundle_root()
    runtime_root = Path.home() / "Library" / "Application Support" / "PV Structure Intelligence Framework"
    runtime_root.mkdir(parents=True, exist_ok=True)
    port = reserve_free_port()
    ...
    process = subprocess.Popen([...])
    install_signal_handlers(lambda *_: terminate_child(process))
    wait_until_healthy(port, timeout_seconds=15)
    subprocess.run(["open", f"http://127.0.0.1:{port}"], check=False)
    process.wait()
```

- [ ] **Step 5: Run launcher tests**

Run: `cd apps/api && uv run pytest tests/test_launcher.py -v`  
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add apps/api/src/api/launcher.py apps/api/src/api/migrations.py apps/api/src/api/config.py apps/api/tests/test_launcher.py
git commit -m "feat: add packaged app launcher"
```

### Task 3: Add macOS Packaging Script And Project Wiring

**Files:**
- Modify: `apps/api/pyproject.toml`
- Modify: `apps/api/uv.lock`
- Create: `scripts/package-macos.sh`
- Modify: `package.json`
- Modify: `README.md`
- Test: manual script dry run

- [ ] **Step 1: Add packaging dependency and command wiring**

```toml
# apps/api/pyproject.toml
[dependency-groups]
dev = [
    ...
    "pyinstaller>=6.13.0",
]
```

```json
// package.json
{
  "scripts": {
    "package:macos": "./scripts/package-macos.sh"
  }
}
```

- [ ] **Step 2: Sync lockfile and verify dependency resolution**

Run: `cd apps/api && uv sync`  
Expected: PASS and `uv.lock` updated with `pyinstaller`.

- [ ] **Step 3: Write the packaging script**

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${ROOT_DIR}/dist/macos"

rm -rf "${DIST_DIR}"
mkdir -p "${DIST_DIR}"

(
  cd "${ROOT_DIR}/apps/web"
  npm run build
)

(
  cd "${ROOT_DIR}/apps/api"
  uv run pyinstaller \
    --noconfirm \
    --windowed \
    --name "PV Structure Intelligence Framework" \
    --add-data "alembic:alembic" \
    --add-data "alembic.ini:." \
    --add-data "../web/dist:web_dist" \
    --add-data "../../data/assets:data/assets" \
    src/api/launcher.py
)
```

- [ ] **Step 4: Update README with packaged app usage**

```md
## macOS 打包

    npm run package:macos

首次打开未签名 `.app` 时，可执行：

    xattr -cr "/path/to/PV Structure Intelligence Framework.app"
```

- [ ] **Step 5: Run packaging script**

Run: `npm run package:macos`  
Expected: PASS and a `.app` appears under `dist/macos` or `apps/api/dist`.

- [ ] **Step 6: Commit**

```bash
git add apps/api/pyproject.toml apps/api/uv.lock package.json scripts/package-macos.sh README.md
git commit -m "build: add macos app packaging"
```

### Task 4: Smoke Test The Packaged App And Document Guardrails

**Files:**
- Modify: `README.md`
- Optionally create: `docs/superpowers/plans/2026-04-05-macos-local-packaging-implementation-plan.md` checkbox updates only
- Test: packaged app manual smoke test

- [ ] **Step 1: Run production-mode smoke test before using the packaged app**

Run:

```bash
cd apps/web && npm run build
cd ../api && uv run python -m api.launcher
```

Expected:
- Browser opens automatically
- Home page loads
- `GET /api/home/recent-records` works

- [ ] **Step 2: Double-click the generated `.app` and run full user flow**

Manual checks:

```text
1. 双击 .app
2. 浏览器自动打开首页
3. 进入 WaterBase workspace
4. 完成 evaluate
5. 保存记录
6. 打开记录详情
7. 导出文件
8. 检查 ~/Library/Application Support/PV Structure Intelligence Framework/runtime/
```

Expected:
- SQLite exists in Application Support
- exports are written outside the `.app`
- quitting the app does not leave the server process running

- [ ] **Step 3: Verify Gatekeeper workaround instructions are accurate**

Run:

```bash
xattr -cr "/path/to/PV Structure Intelligence Framework.app"
```

Expected: command succeeds and the app opens afterward if quarantine was present.

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: add macos packaging smoke test guidance"
```

---

## Self-Review

- Spec coverage: this plan covers production-mode single-port serving, launcher path resolution, signal cleanup, dynamic port selection, PyInstaller packaging, Gatekeeper guidance, and smoke testing.
- Placeholder scan: each task has files, commands, and expected outcomes; no unresolved placeholders remain.
- Type consistency: launcher, migration config, and packaging script all assume absolute resource paths and one FastAPI production service; no alternate runtime path model is introduced later in the plan.
