from __future__ import annotations

import importlib.util
from pathlib import Path
import signal
import subprocess
import sys
import socket
import time

from api.launcher import (
    LauncherPaths,
    build_cleanup,
    build_launcher_settings,
    build_server_command,
    build_server_environment,
    install_signal_handlers,
    launch_app,
    open_browser,
    prepare_runtime_paths,
    reserve_free_port,
    resolve_bundle_root,
    wait_until_healthy,
)


class FakeProcess:
    def __init__(self) -> None:
        self.terminated = False
        self.killed = False
        self.wait_calls: list[float | None] = []
        self._poll_result: int | None = None

    def poll(self) -> int | None:
        return self._poll_result

    def terminate(self) -> None:
        self.terminated = True

    def kill(self) -> None:
        self.killed = True

    def wait(self, timeout: float | None = None) -> int:
        self.wait_calls.append(timeout)
        return 0


class TimeoutProcess(FakeProcess):
    def wait(self, timeout: float | None = None) -> int:
        self.wait_calls.append(timeout)
        raise subprocess.TimeoutExpired(cmd=["launcher"], timeout=timeout or 0)


def test_resolve_bundle_root_prefers_meipass(monkeypatch) -> None:
    bundle_root = Path("/tmp/bundle-root")
    monkeypatch.setattr(sys, "_MEIPASS", str(bundle_root), raising=False)

    assert resolve_bundle_root() == bundle_root


def test_launcher_supports_script_style_import(monkeypatch) -> None:
    launcher_path = Path(__file__).resolve().parents[1] / "src" / "api" / "launcher.py"
    monkeypatch.syspath_prepend(str(launcher_path.parents[1]))
    spec = importlib.util.spec_from_file_location("launcher_standalone_test", launcher_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.delitem(sys.modules, "api.main", raising=False)
    monkeypatch.setitem(sys.modules, spec.name, module)

    spec.loader.exec_module(module)

    assert module.APP_SUPPORT_DIR_NAME == "PV Structure Intelligence Framework"
    assert "api.main" not in sys.modules


def test_reserve_free_port_returns_positive_port() -> None:
    port = reserve_free_port()

    assert isinstance(port, int)
    assert port > 0


def test_install_signal_handlers_registers_sigterm_and_sigint(monkeypatch) -> None:
    registered: dict[int, object] = {}
    cleanup_calls: list[str] = []

    def fake_signal(signum: int, handler: object) -> None:
        registered[signum] = handler

    def cleanup() -> None:
        cleanup_calls.append("cleanup")

    monkeypatch.setattr(signal, "signal", fake_signal)

    install_signal_handlers(cleanup)

    assert signal.SIGTERM in registered
    assert signal.SIGINT in registered
    registered[signal.SIGTERM](signal.SIGTERM, None)
    registered[signal.SIGINT](signal.SIGINT, None)
    assert cleanup_calls == ["cleanup", "cleanup"]


def test_build_server_command_uses_launcher_entrypoint_and_dynamic_port() -> None:
    command = build_server_command(43210)

    assert command[0] == sys.executable
    assert command[1:4] == ["-m", "api.launcher", "--serve"]
    assert command[-2:] == ["--port", "43210"]
    assert "--app-dir" not in command


def test_build_server_command_uses_same_executable_when_frozen(monkeypatch) -> None:
    monkeypatch.setattr(sys, "frozen", True, raising=False)

    command = build_server_command(43210)

    assert command == [sys.executable, "--serve", "--port", "43210"]


def test_build_server_environment_uses_absolute_runtime_paths(tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle"
    (bundle_root / "web_dist").mkdir(parents=True, exist_ok=True)
    runtime_root = tmp_path / "runtime-root"
    paths = prepare_runtime_paths(bundle_root, runtime_root)

    env = build_server_environment(paths)

    assert env["WORKING_TOOL_ASSETS_DIR"] == str(bundle_root / "data" / "assets")
    assert env["WORKING_TOOL_RUNTIME_DIR"] == str(paths.runtime_dir)
    assert env["WORKING_TOOL_EXPORTS_DIR"] == str(paths.exports_dir)
    assert env["WORKING_TOOL_WEB_DIST_DIR"] == str(bundle_root / "web_dist")


def test_build_launcher_settings_uses_bundle_paths(tmp_path: Path) -> None:
    paths = LauncherPaths(
        bundle_root=tmp_path / "bundle",
        runtime_root=tmp_path / "home" / "Library" / "Application Support" / "PV Structure Intelligence Framework",
        runtime_dir=tmp_path / "runtime",
        exports_dir=tmp_path / "runtime" / "exports",
        web_dist_dir=tmp_path / "bundle" / "web_dist",
    )

    settings = build_launcher_settings(paths)

    assert settings.assets_dir == paths.bundle_root / "data" / "assets"
    assert settings.runtime_dir == paths.runtime_dir
    assert settings.exports_dir == paths.exports_dir
    assert settings.web_dist_dir == paths.web_dist_dir


def test_open_browser_targets_selected_port(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run(command: list[str], check: bool) -> None:
        calls.append(command)
        assert check is False

    monkeypatch.setattr(subprocess, "run", fake_run)

    open_browser(45678)

    assert calls == [["open", "http://127.0.0.1:45678"]]


def test_wait_until_healthy_retries_until_socket_accepts(monkeypatch) -> None:
    attempts = {"count": 0}
    ticks = iter([0.0, 0.01, 0.02, 0.03])

    def fake_create_connection(address, timeout):  # noqa: ANN001
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise OSError("not ready")

        class Connection:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        return Connection()

    monkeypatch.setattr(socket, "create_connection", fake_create_connection)
    monkeypatch.setattr(time, "monotonic", lambda: next(ticks))
    monkeypatch.setattr(time, "sleep", lambda _: None)

    wait_until_healthy(12345, timeout_seconds=1, poll_interval_seconds=0.01)

    assert attempts["count"] == 3


def test_build_cleanup_terminates_running_process() -> None:
    process = FakeProcess()

    cleanup = build_cleanup(process)  # type: ignore[arg-type]
    cleanup()

    assert process.terminated is True
    assert process.wait_calls == [5]


def test_build_cleanup_kills_child_when_terminate_times_out() -> None:
    process = TimeoutProcess()

    cleanup = build_cleanup(process)  # type: ignore[arg-type]
    cleanup()

    assert process.terminated is True
    assert process.killed is True
    assert process.wait_calls == [5, 5]


def test_launch_app_wires_port_paths_and_browser(monkeypatch, tmp_path: Path) -> None:
    bundle_root = tmp_path / "bundle"
    home_dir = tmp_path / "home"
    captured: dict[str, object] = {}
    process = FakeProcess()

    def fake_port_reserver() -> int:
        return 54321

    def fake_process_starter(paths: LauncherPaths, port: int) -> FakeProcess:
        captured["paths"] = paths
        captured["port"] = port
        return process

    def fake_readiness_waiter(port: int) -> None:
        captured["ready_port"] = port

    def fake_browser_opener(port: int) -> None:
        captured["browser_port"] = port

    def fake_signal_installer(cleanup) -> None:
        captured["cleanup"] = cleanup

    def fake_database_upgrader(settings, *, bundle_root: Path) -> None:
        captured["settings"] = settings
        captured["bundle_root"] = bundle_root

    def fake_wait(timeout: float | None = None) -> int:
        process.wait_calls.append(timeout)
        process._poll_result = 0
        return 0

    process.wait = fake_wait  # type: ignore[assignment]

    exit_code = launch_app(
        bundle_root=bundle_root,
        home_dir=home_dir,
        port_reserver=fake_port_reserver,
        process_starter=fake_process_starter,
        readiness_waiter=fake_readiness_waiter,
        browser_opener=fake_browser_opener,
        signal_installer=fake_signal_installer,
        database_upgrader=fake_database_upgrader,
    )

    assert exit_code == 0
    assert captured["port"] == 54321
    assert captured["ready_port"] == 54321
    assert captured["browser_port"] == 54321
    paths = captured["paths"]
    assert isinstance(paths, LauncherPaths)
    assert paths.runtime_root == home_dir / "Library" / "Application Support" / "PV Structure Intelligence Framework"
    assert paths.runtime_dir == paths.runtime_root / "runtime"
    assert paths.exports_dir == paths.runtime_dir / "exports"
    assert paths.web_dist_dir == bundle_root / "web_dist"
    assert paths.runtime_dir.exists()
    assert paths.exports_dir.exists()
    settings = captured["settings"]
    assert settings.runtime_dir == paths.runtime_dir
    assert settings.exports_dir == paths.exports_dir
    assert captured["bundle_root"] == bundle_root
