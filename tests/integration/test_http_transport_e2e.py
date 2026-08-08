"""Real HTTP transport process-lifecycle tests.

Spawns the actual server binary over the streamable-HTTP transport and
verifies session lifecycle, concurrency, and shutdown against the real
process rather than mocks. No test here calls a yfinance-backed tool, so
none of it needs network access or the `live` marker.

core/server.py's run_http_server wraps mcp.run() in
except KeyboardInterrupt / except Exception, but uvicorn.Server installs
its own SIGINT/SIGTERM handlers and calls sys.exit() directly for both
graceful shutdown and startup failures - confirmed here against a real
process, not a mock of mcp.run(). test_run_http_server_keyboard in
tests/core/test_server.py verifies that branch as written; this file
verifies what a real SIGINT/SIGTERM actually does.
"""

import http.client
import json
import os
import signal
import socket
import subprocess
import sys
import time

import pytest

pytestmark = pytest.mark.asyncio


def _free_port() -> int:
    """Return a port that was free a moment ago.

    Inherently racy: the socket must be closed before the server can bind
    the port, so another process - notably a concurrent xdist worker, since
    addopts includes -n auto - can take it in between. The http_server
    fixture retries on that rather than failing the test.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_port(port: int, timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.2)
    raise TimeoutError(f"Server did not start listening on port {port} within {timeout}s")


def _post(port: int, payload: dict, session_id: str | None = None) -> tuple[int, dict, dict]:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if session_id:
        headers["mcp-session-id"] = session_id
    try:
        conn.request("POST", "/mcp", body=json.dumps(payload), headers=headers)
        response = conn.getresponse()
        body = response.read().decode()
        response_headers = dict(response.getheaders())
        parsed = {}
        for line in body.splitlines():
            if line.startswith("data:"):
                parsed = json.loads(line[len("data:") :].strip())
                break
        return response.status, response_headers, parsed
    finally:
        conn.close()


def _initialize_session(port: int) -> str:
    status, headers, _ = _post(
        port,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "0"},
            },
        },
    )
    assert status == 200
    session_id = headers["mcp-session-id"]
    _post(port, {"jsonrpc": "2.0", "method": "notifications/initialized"}, session_id=session_id)
    return session_id


def _terminate(process: subprocess.Popen) -> None:
    """Stop a server process, escalating to kill if it does not exit."""
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def _close_pipes(process: subprocess.Popen) -> None:
    """Close the process's stdout/stderr pipes.

    Popen is used without a context manager here so the fixture can retry,
    so the pipes must be closed explicitly to avoid a ResourceWarning.
    """
    for stream in (process.stdout, process.stderr):
        if stream is not None:
            stream.close()


@pytest.fixture
def http_server():
    """Start a real server on a free port, retrying if the port is stolen.

    _free_port cannot hold the port open, so a concurrent xdist worker can
    claim it before the server binds. Retrying keeps this fixture from
    failing intermittently under the default -n auto.
    """
    attempts = 3
    for attempt in range(1, attempts + 1):
        port = _free_port()
        process = subprocess.Popen(
            ["uv", "run", "openmarkets", "--transport", "http", "--port", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            _wait_for_port(port)
        except TimeoutError:
            _terminate(process)
            stderr = process.stderr.read() if process.stderr else ""
            _close_pipes(process)
            if "address already in use" in stderr.lower() and attempt < attempts:
                continue
            raise

        try:
            yield port, process
        finally:
            _terminate(process)
            _close_pipes(process)
        return


async def test_session_delete_actually_invalidates_the_session(http_server):
    """DELETE must make the session unusable for any further request."""
    port, _ = http_server
    session_id = _initialize_session(port)

    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    try:
        conn.request("DELETE", "/mcp", headers={"mcp-session-id": session_id})
        delete_status = conn.getresponse().status
    finally:
        conn.close()
    assert delete_status == 200

    status, _, _ = _post(port, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, session_id=session_id)
    assert status == 404


async def test_two_sessions_are_independent(http_server):
    """Two clients initializing concurrently must get distinct sessions,
    and each session's requests must not interfere with the other's."""
    port, _ = http_server
    session_a = _initialize_session(port)
    session_b = _initialize_session(port)

    assert session_a != session_b

    status_a, _, result_a = _post(port, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, session_id=session_a)
    status_b, _, result_b = _post(port, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, session_id=session_b)

    assert status_a == 200
    assert status_b == 200
    assert len(result_a["result"]["tools"]) == len(result_b["result"]["tools"])


def _assert_terminated_by_sigterm_after_graceful_shutdown(process: subprocess.Popen) -> None:
    """Assert the process exited via SIGTERM's default disposition, not a crash.

    uvicorn.Server installs its own SIGTERM/SIGINT handlers, runs its
    shutdown sequence, then re-delivers the raw OS signal via
    signal.raise_signal() rather than calling sys.exit(0) - confirmed by
    reading uvicorn's own source (Server.capture_signals) and reproducing
    it here. That makes the process exit code 128 + SIGTERM (143), not 0,
    even though the shutdown itself is completely clean - this is standard
    POSIX signal-exit behaviour that orchestrators (Kubernetes, Docker,
    systemd) already treat as a successful graceful stop, not a crash.
    An initial version of this test asserted exit_code == 0, which is
    incorrect for the real process; verified directly against both `uv run
    openmarkets` and the installed console-script binary.

    Args:
        process: The terminated subprocess.
    """
    assert process.returncode == 128 + signal.SIGTERM
    stderr = process.stderr.read() if process.stderr else ""
    assert "Traceback" not in stderr
    assert "Application shutdown complete" in stderr


@pytest.mark.skipif(
    sys.platform == "win32",
    reason=(
        "POSIX signal semantics: on Windows Popen.send_signal(SIGTERM) maps to "
        "TerminateProcess, so no signal is delivered, uvicorn's handler never runs, "
        "and the exit code is not 128 + SIGTERM."
    ),
)
async def test_sigterm_shuts_down_gracefully(http_server):
    """A real SIGTERM must run the full graceful-shutdown sequence, not hang
    or crash - verified against the actual process, not the except
    KeyboardInterrupt branch in run_http_server, which never fires here.
    """
    port, process = http_server
    _initialize_session(port)

    process.send_signal(signal.SIGTERM)
    process.wait(timeout=10)

    _assert_terminated_by_sigterm_after_graceful_shutdown(process)


@pytest.mark.skipif(
    sys.platform == "win32",
    reason=(
        "POSIX signal semantics: on Windows Popen.send_signal(SIGTERM) maps to "
        "TerminateProcess, so no signal is delivered, uvicorn's handler never runs, "
        "and the exit code is not 128 + SIGTERM."
    ),
)
async def test_sigterm_during_an_open_session_still_exits_cleanly(http_server):
    """A signal arriving while a session is open must not hang the
    shutdown and must not leave the process running."""
    port, process = http_server
    session_id = _initialize_session(port)

    status, _, _ = _post(port, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, session_id=session_id)
    assert status == 200

    process.send_signal(signal.SIGTERM)
    process.wait(timeout=10)

    _assert_terminated_by_sigterm_after_graceful_shutdown(process)
    assert process.poll() is not None


async def test_bind_conflict_on_an_occupied_port_exits_non_zero(http_server):
    """Starting a second server on the same port must fail cleanly, not
    hang or silently succeed - this is uvicorn's own sys.exit(3) path,
    which bypasses our except Exception branch entirely.

    Asserts on the specific bind error rather than just a non-zero exit:
    a bare `!= 0` would pass for the wrong reason if the second process
    died for any unrelated cause (a missing dependency, an import error,
    a port stolen by a concurrent xdist worker).
    """
    port, _ = http_server

    with subprocess.Popen(
        ["uv", "run", "openmarkets", "--transport", "http", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    ) as conflicting:
        try:
            exit_code = conflicting.wait(timeout=15)
            stderr = conflicting.stderr.read() if conflicting.stderr else ""

            assert exit_code != 0
            assert "address already in use" in stderr.lower()
        finally:
            if conflicting.poll() is None:
                conflicting.terminate()
                conflicting.wait(timeout=5)
