import os
import subprocess
from pathlib import Path

from tests.acceptance.sc_001.fixtures import running_system, unreachable_base_url

ROOT = Path(__file__).resolve().parents[3]
CLIENT = ROOT / "client/worklog-cli"


def test_sc001_ex02_cli_reports_started_activity() -> None:
    with running_system() as system:
        result = run_cli(system.base_url, "設計を書く")

    assert result.returncode == 0
    assert result.stdout == "開始: 設計を書く\n"
    assert result.stderr == ""


def test_sc001_ex04_cli_rejects_empty_title() -> None:
    with unreachable_base_url() as base_url:
        result = run_cli(base_url, "   ")

    assert result.returncode != 0
    assert result.stdout == ""
    assert "作業名を空にはできません" in result.stderr


def test_sc001_ex05_cli_reports_unreachable_backend() -> None:
    with unreachable_base_url() as base_url:
        result = run_cli(base_url, "設計を書く")

    assert result.returncode != 0
    assert result.stdout == ""
    assert "バックエンドへ作業開始を依頼できません" in result.stderr


def run_cli(base_url: str, title: str) -> subprocess.CompletedProcess[str]:
    environment = {**os.environ, "WORKLOG_API_BASE_URL": base_url}
    return subprocess.run(
        ["go", "run", "./cmd/worklog", "start", title],
        cwd=CLIENT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
