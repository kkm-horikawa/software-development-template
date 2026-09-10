import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_st003_go_client_starts_activity_through_fastapi() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/exercise-platforms.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.splitlines() == [
        "Go client -> FastAPI: 開始: 設計を書く",
        "SQLAlchemy保存件数: 1",
    ]
