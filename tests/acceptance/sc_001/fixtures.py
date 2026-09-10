from __future__ import annotations

import socket
import tempfile
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from uuid import UUID

import uvicorn
from sqlalchemy import create_engine
from worklog.main import ApplicationFactory


@dataclass(frozen=True)
class RunningSystem:
    base_url: str


@contextmanager
def running_system(storage_failure: bool = False) -> Iterator[RunningSystem]:
    with tempfile.TemporaryDirectory() as directory:
        database = create_engine(f"sqlite:///{directory}/activities.sqlite3")
        app = ApplicationFactory(
            engine=database,
            clock=lambda: datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
            new_id=lambda: UUID("11111111-1111-1111-1111-111111111111"),
        ).create()
        if storage_failure:
            with database.begin() as connection:
                connection.exec_driver_sql(
                    "CREATE TRIGGER reject_activity BEFORE INSERT ON activities "
                    "BEGIN SELECT RAISE(ABORT, 'test storage failure'); END"
                )
        port = available_port()
        server = uvicorn.Server(
            uvicorn.Config(app, host="127.0.0.1", port=port, log_level="critical")
        )
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        try:
            wait_until_started(server)
            yield RunningSystem(base_url=f"http://127.0.0.1:{port}")
        finally:
            server.should_exit = True
            thread.join(timeout=5)
            database.dispose()


@contextmanager
def unreachable_base_url() -> Iterator[str]:
    with socket.socket() as reserved:
        reserved.bind(("127.0.0.1", 0))
        port = int(reserved.getsockname()[1])
        yield f"http://127.0.0.1:{port}"


def available_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def wait_until_started(server: uvicorn.Server) -> None:
    for _ in range(200):
        if server.started:
            return
        time.sleep(0.01)
    raise RuntimeError("FastAPIを起動できませんでした")


class FaultyResponseHandler(BaseHTTPRequestHandler):
    lose_response = False

    def do_POST(self) -> None:
        self.rfile.read(int(self.headers.get("Content-Length", "0")))
        if self.lose_response:
            self.close_connection = True
            return
        self.send_response(201)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write('{"title":"設計を書く"}'.encode())

    def log_message(self, _format: str, *args: object) -> None:
        pass


class LostResponseHandler(FaultyResponseHandler):
    lose_response = True


@contextmanager
def faulty_backend(lose_response: bool = False) -> Iterator[str]:
    handler = LostResponseHandler if lose_response else FaultyResponseHandler
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
