import os
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

from tests.acceptance.sc_001.cases import BackendState, CLIStartCase, CLIStartCases
from tests.acceptance.sc_001.fixtures import (
    faulty_backend,
    running_system,
    unreachable_base_url,
)

ROOT = Path(__file__).resolve().parents[3]
CLIENT = ROOT / "client/worklog-cli"


class TestCLIStartActivity:
    @pytest.mark.parametrize(
        "case",
        CLIStartCases(Path(__file__).with_name("task.csv")).load(),
        ids=lambda case: case.case_id,
    )
    def test_cli_start_activity(self, case: CLIStartCase) -> None:
        with self.backend(case.backend_state) as base_url:
            result = self.run_cli(base_url, case.title)

        assert (result.returncode == 0) == case.expected_success
        assert result.stdout == case.stdout()
        if case.expected_error:
            assert case.expected_error in result.stderr
        else:
            assert result.stderr == ""

    @contextmanager
    def backend(self, state: BackendState) -> Iterator[str]:
        if state in {BackendState.RUNNING, BackendState.STORAGE_FAILURE}:
            with running_system(
                storage_failure=state is BackendState.STORAGE_FAILURE
            ) as system:
                yield system.base_url
        elif state is BackendState.UNREACHABLE:
            with unreachable_base_url() as base_url:
                yield base_url
        else:
            with faulty_backend(
                lose_response=state is BackendState.LOST_RESPONSE
            ) as base_url:
                yield base_url

    def run_cli(self, base_url: str, title: str) -> subprocess.CompletedProcess[str]:
        environment = {**os.environ, "WORKLOG_API_BASE_URL": base_url}
        return subprocess.run(
            ["go", "run", "./cmd/worklog", "start", title],
            cwd=CLIENT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
