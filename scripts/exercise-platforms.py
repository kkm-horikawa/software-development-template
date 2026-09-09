#!/usr/bin/env python3
from __future__ import annotations

import os
import socket
import subprocess
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import uvicorn
from sqlalchemy import create_engine
from worklog.main import create_app

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "client/worklog-cli"


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


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        database = create_engine(f"sqlite:///{directory}/activities.sqlite3")
        app = create_app(
            engine=database,
            clock=lambda: datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc),
            new_id=lambda: UUID("11111111-1111-1111-1111-111111111111"),
        )
        port = available_port()
        server = uvicorn.Server(
            uvicorn.Config(app, host="127.0.0.1", port=port, log_level="critical")
        )
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        try:
            wait_until_started(server)
            environment = {
                **os.environ,
                "WORKLOG_API_BASE_URL": f"http://127.0.0.1:{port}",
            }
            result = subprocess.run(
                ["go", "run", "./cmd/worklog", "start", "設計を書く"],
                cwd=CLIENT,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
        finally:
            server.should_exit = True
            thread.join(timeout=5)

        output = result.stdout.strip()
        saved = len(app.state.activity_repository.all())
        if output != "開始: 設計を書く" or saved != 1:
            raise RuntimeError(f"連携結果が不正です: output={output!r}, saved={saved}")
        print(f"Go client -> FastAPI: {output}")
        print(f"SQLAlchemy保存件数: {saved}")


if __name__ == "__main__":
    main()
