#!/usr/bin/env python3
"""必要な文書と、Markdown内の相対リンクを検査する。"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRECTORIES = {".git", ".pytest_cache", ".venv", "__pycache__"}
REQUIRED_FILES = (
    "README.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "docs/000_process.md",
    "docs/010_design-principles.md",
    "docs/020_code-structure.md",
    "docs/030_testing.md",
    "docs/040_completion.md",
    "docs/100_requirements.md",
    "docs/increments/_template.md",
    "docs/decisions/_template.md",
    "examples/python/fastapi/README.md",
    "examples/python/fastapi/pyproject.toml",
    "examples/python/fastapi/uv.lock",
    "examples/go/topdown/README.md",
    "examples/go/topdown/go.mod",
    ".github/workflows/check.yml",
    "scripts/check-all.sh",
    "scripts/check-trace.py",
    ".github/ISSUE_TEMPLATE/change.yml",
    ".github/pull_request_template.md",
)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def missing_required_files() -> list[str]:
    return [name for name in REQUIRED_FILES if not (ROOT / name).is_file()]


def broken_links() -> list[str]:
    broken: list[str] = []
    for document in sorted(ROOT.rglob("*.md")):
        if any(part in SKIP_DIRECTORIES for part in document.parts):
            continue
        for raw_target in LINK.findall(document.read_text(encoding="utf-8")):
            target = raw_target.strip().strip("<>")
            if target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            path_part = unquote(target.split("#", 1)[0])
            if not path_part:
                continue
            resolved = (document.parent / path_part).resolve()
            if not resolved.exists():
                relative_document = document.relative_to(ROOT)
                broken.append(f"{relative_document}: {target}")
    return broken


def main() -> int:
    failures = [
        *(f"必要なファイルがありません: {name}" for name in missing_required_files()),
        *(f"リンク先がありません: {link}" for link in broken_links()),
    ]
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("文書の構造: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
