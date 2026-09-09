default:
    @just --list

check:
    @./scripts/check-all.sh

check-docs:
    @python3 scripts/check-docs.py

check-trace:
    @python3 scripts/check-trace.py

check-secrets:
    @python3 scripts/check-secrets.py

check-python:
    @uv run --project examples/python/fastapi ruff check examples/python/fastapi scripts >/dev/null
    @uv run --project examples/python/fastapi ruff format --check examples/python/fastapi scripts >/dev/null
    @echo 'Python静的検査: OK'

check-fastapi-example:
    @uv run --project examples/python/fastapi pytest examples/python/fastapi/tests -q -k 'not method_flow' >/dev/null
    @uv run --project examples/python/fastapi python examples/python/fastapi/scripts/exercise_api.py >/dev/null
    @echo 'FastAPI実例: OK'

check-go-example:
    @cd examples/go/topdown && go test ./... >/dev/null
    @output="$$(cd examples/go/topdown && go run ./cmd/example start '設計を書く')"; test "$$output" = '開始: 設計を書く'
    @echo 'Go実例: OK'

check-method-flow:
    @uv run --project examples/python/fastapi pytest examples/python/fastapi/tests/test_method_flow.py -q >/dev/null
    @cd examples/go/topdown && go test ./internal/architecture -run 'TestMethodFlow' >/dev/null
    @echo 'トップダウン構造: OK'

example:
    @uv run --project examples/python/fastapi python examples/python/fastapi/scripts/exercise_api.py

example-go:
    @cd examples/go/topdown && go run ./cmd/example start '設計を書く'
