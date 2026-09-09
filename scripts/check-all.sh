#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root_dir"

python3 scripts/check-docs.py
python3 scripts/check-trace.py
python3 scripts/check-secrets.py

uv run --project examples/python/fastapi ruff check examples/python/fastapi scripts >/dev/null
uv run --project examples/python/fastapi ruff format --check examples/python/fastapi scripts >/dev/null
echo 'Python静的検査: OK'

uv run --project examples/python/fastapi pytest examples/python/fastapi/tests -q -k 'not method_flow' >/dev/null
uv run --project examples/python/fastapi python examples/python/fastapi/scripts/exercise_api.py >/dev/null
echo 'FastAPI実例: OK'

(
  cd examples/go/topdown
  go test ./... >/dev/null
  output="$(go run ./cmd/example start '設計を書く')"
  test "$output" = '開始: 設計を書く'
)
echo 'Go実例: OK'

uv run --project examples/python/fastapi pytest examples/python/fastapi/tests/test_method_flow.py -q >/dev/null
(cd examples/go/topdown && go test ./internal/architecture -run 'TestMethodFlow' >/dev/null)
echo 'トップダウン構造: OK'
