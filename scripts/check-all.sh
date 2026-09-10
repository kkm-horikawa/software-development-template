#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

python3 scripts/check-docs.py
python3 scripts/check-trace.py
uv run --project backend/worklog-api pytest scripts/tests -q >/dev/null
python3 scripts/check-secrets.py

uv run --project backend/worklog-api ruff check backend/worklog-api scripts >/dev/null
uv run --project backend/worklog-api ruff format --check backend/worklog-api scripts >/dev/null
echo 'Python静的検査: OK'

uv run --project backend/worklog-api pytest backend/worklog-api/tests -q -k 'not method_flow and not platform_flow' >/dev/null
uv run --project backend/worklog-api python backend/worklog-api/scripts/exercise_api.py >/dev/null
echo 'バックエンド実例: OK'

(
  cd client/worklog-cli
  go test ./... >/dev/null
)
echo 'Goクライアント実例: OK'

PYTHONPATH=backend/worklog-api/src uv run --project backend/worklog-api \
  pytest backend/worklog-api/tests/test_platform_flow.py -q >/dev/null
echo 'バックエンド・クライアント連携: OK'

uv run --project backend/worklog-api pytest backend/worklog-api/tests/test_method_flow.py -q >/dev/null
(cd client/worklog-cli && go test ./internal/architecture -run 'TestMethodFlow' >/dev/null)
echo 'トップダウン構造: OK'
