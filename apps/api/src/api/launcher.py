from __future__ import annotations

from dataclasses import dataclass
import argparse
from pathlib import Path
import os
import signal
import socket
import subprocess
import sys
import time
from typing import Callable

try:
    from .config import Settings
    from .migrations import upgrade_database
except ImportError:
    from api.config import Settings
    from api.migrations import upgrade_database

APP_SUPPORT_DIR_NAME = "PV Structure Intelligence Framework"
LAUNCHER_HOST = "127.0.0.1"
LAUNCHER_TIMEOUT_SECONDS = 15.0
LAUNCHER_POLL_INTERVAL_SECONDS = 0.1


@dataclass(frozen=True)
class LauncherPaths:
    bundle_root: Path
    runtime_root: Path
    runtime_dir: Path
    exports_dir: Path
    web_dist_dir: Path


def build_launcher_settings(paths: LauncherPaths) -> Settings:
    return Settings(
        assets_dir=paths.bundle_root / "data" / "assets",
        runtime_dir=paths.runtime_dir,
        exports_dir=paths.exports_dir,
        web_dist_dir=paths.web_dist_dir,
    )


def resolve_bundle_root() -> Path:
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root)
    return Path(__file__).resolve().parents[2]


def resolve_runtime_root(home_dir: Path | None = None) -> Path:
    root_dir = home_dir or Path.home()
    return root_dir / "Library" / "Application Support" / APP_SUPPORT_DIR_NAME


def prepare_runtime_paths(bundle_root: Path, runtime_root: Path) -> LauncherPaths:
    runtime_dir = runtime_root / "runtime"
    exports_dir = runtime_dir / "exports"
    web_dist_dir = resolve_web_dist_dir(bundle_root)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    exports_dir.mkdir(parents=True, exist_ok=True)
    return LauncherPaths(
        bundle_root=bundle_root,
        runtime_root=runtime_root,
        runtime_dir=runtime_dir,
        exports_dir=exports_dir,
        web_dist_dir=web_dist_dir,
    )


def resolve_web_dist_dir(bundle_root: Path) -> Path:
    packaged_web_dist_dir = bundle_root / "web_dist"
    if packaged_web_dist_dir.exists():
        return packaged_web_dist_dir

    source_web_dist_dir = bundle_root.parent.parent / "apps" / "web" / "dist"
    if source_web_dist_dir.exists():
        return source_web_dist_dir

    return packaged_web_dist_dir


def reserve_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((LAUNCHER_HOST, 0))
        return int(sock.getsockname()[1])


def install_signal_handlers(cleanup: Callable[[], None]) -> None:
    def _handle_signal(signum: int, frame: object) -> None:  # noqa: ARG001
        cleanup()

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)


def build_server_command(port: int) -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable, "--serve", "--port", str(port)]
    return [sys.executable, "-m", "api.launcher", "--serve", "--port", str(port)]


def build_server_environment(paths: LauncherPaths) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "WORKING_TOOL_ASSETS_DIR": str(paths.bundle_root / "data" / "assets"),
            "WORKING_TOOL_RUNTIME_DIR": str(paths.runtime_dir),
            "WORKING_TOOL_EXPORTS_DIR": str(paths.exports_dir),
            "WORKING_TOOL_WEB_DIST_DIR": str(paths.web_dist_dir),
        }
    )
    return env


def start_server_process(paths: LauncherPaths, port: int) -> subprocess.Popen[str]:
    command = build_server_command(port)
    environment = build_server_environment(paths)
    return subprocess.Popen(command, cwd=str(paths.bundle_root), env=environment)


def wait_until_healthy(
    port: int,
    *,
    timeout_seconds: float = LAUNCHER_TIMEOUT_SECONDS,
    poll_interval_seconds: float = LAUNCHER_POLL_INTERVAL_SECONDS,
) -> None:
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            with socket.create_connection((LAUNCHER_HOST, port), timeout=poll_interval_seconds):
                return
        except OSError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Server on port {port} did not become ready within {timeout_seconds:g} seconds")
            time.sleep(poll_interval_seconds)


def open_browser(port: int) -> None:
    subprocess.run(["open", f"http://127.0.0.1:{port}"], check=False)


def terminate_child(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            return


def build_cleanup(process: subprocess.Popen[str]) -> Callable[[], None]:
    def cleanup() -> None:
        terminate_child(process)

    return cleanup


def launch_app(
    *,
    bundle_root: Path | None = None,
    home_dir: Path | None = None,
    port_reserver: Callable[[], int] = reserve_free_port,
    process_starter: Callable[[LauncherPaths, int], subprocess.Popen[str]] = start_server_process,
    readiness_waiter: Callable[[int], None] = wait_until_healthy,
    browser_opener: Callable[[int], None] = open_browser,
    signal_installer: Callable[[Callable[[], None]], None] = install_signal_handlers,
    database_upgrader: Callable[..., None] = upgrade_database,
) -> int:
    resolved_bundle_root = bundle_root or resolve_bundle_root()
    runtime_root = resolve_runtime_root(home_dir)
    paths = prepare_runtime_paths(resolved_bundle_root, runtime_root)
    settings = build_launcher_settings(paths)
    database_upgrader(settings, bundle_root=resolved_bundle_root)
    port = port_reserver()
    process = process_starter(paths, port)
    cleanup = build_cleanup(process)
    signal_installer(cleanup)
    try:
        readiness_waiter(port)
        browser_opener(port)
        return process.wait()
    finally:
        cleanup()


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int)
    args = parser.parse_args()
    if args.serve:
        if args.port is None:
            raise SystemExit("--port is required in serve mode")
        return serve_app(args.port)
    return launch_app()


def serve_app(port: int) -> int:
    try:
        from .main import create_app
    except ImportError:
        from api.main import create_app

    app = create_app()
    import uvicorn

    uvicorn.run(app, host=LAUNCHER_HOST, port=port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
