default:
    @just --list

check:
    @./scripts/check-all.sh

check-docs:
    @python3 scripts/check-docs.py
    @uv run --project backend/worklog-api pytest scripts/tests -q >/dev/null

check-trace:
    @python3 scripts/check-trace.py

check-secrets:
    @python3 scripts/check-secrets.py

check-python:
    @uv run --project backend/worklog-api ruff check backend/worklog-api scripts tests >/dev/null
    @uv run --project backend/worklog-api ruff format --check backend/worklog-api scripts tests >/dev/null
    @echo 'Python静的検査: OK'

check-fastapi-example:
    @uv run --project backend/worklog-api pytest backend/worklog-api/tests -q -k 'not method_flow' >/dev/null
    @uv run --project backend/worklog-api python backend/worklog-api/scripts/exercise_api.py >/dev/null
    @echo 'バックエンド実例: OK'

check-go-example:
    @cd client/worklog-cli && go test ./... >/dev/null
    @echo 'Goクライアント実例: OK'

check-platform-example:
    @PYTHONPATH=backend/worklog-api/src uv run --project backend/worklog-api pytest tests/acceptance -q >/dev/null
    @echo '受入テスト: OK'

check-method-flow:
    @uv run --project backend/worklog-api pytest backend/worklog-api/tests/test_method_flow.py -q >/dev/null
    @cd client/worklog-cli && go test ./internal/architecture -run 'TestMethodFlow' >/dev/null
    @echo 'トップダウン構造: OK'

example:
    @uv run --project backend/worklog-api python backend/worklog-api/scripts/exercise_api.py

example-go:
    @PYTHONPATH=backend/worklog-api/src uv run --project backend/worklog-api python scripts/exercise-platforms.py
