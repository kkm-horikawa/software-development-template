#!/usr/bin/env python3
"""要求から実在するシステム・結合テストまでの参照を検算する。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRECTORIES = {".git", ".pytest_cache", ".venv", "__pycache__"}
DEFINITION = re.compile(r"^#{2,6}\s+((?:PB|SC|REQ|AC|SPEC|ST|AD|IT)-\d{3})\b")
REFERENCE = re.compile(r"\[((?:PB|SC|REQ|AC|SPEC|ST|AD|IT)-\d{3})\]")
EXPECTED_PARENT = {
    "SC": "PB",
    "REQ": "SC",
    "AC": "REQ",
    "SPEC": "AC",
    "ST": "SPEC",
    "AD": "SPEC",
    "IT": "AD",
}


def trace_documents() -> list[Path]:
    documents = [ROOT / "docs/100_requirements.md"]
    documents.extend(
        path
        for path in sorted((ROOT / "docs/increments").glob("*.md"))
        if not path.name.startswith("_") and path.name != "README.md"
    )
    return documents


def definitions() -> tuple[dict[str, tuple[Path, int, set[str]]], list[str]]:
    found: dict[str, tuple[Path, int, set[str]]] = {}
    failures: list[str] = []
    for document in trace_documents():
        for line_number, line in enumerate(
            document.read_text(encoding="utf-8").splitlines(), 1
        ):
            match = DEFINITION.match(line)
            if not match:
                continue
            identifier = match.group(1)
            if identifier in found:
                failures.append(f"{identifier} が二重に定義されています")
                continue
            found[identifier] = (document, line_number, set(REFERENCE.findall(line)))
    return found, failures


def test_sources() -> str:
    contents: list[str] = []
    for pattern in ("**/test_*.py", "**/*_test.go"):
        for path in ROOT.glob(pattern):
            if not any(part in SKIP_DIRECTORIES for part in path.parts):
                contents.append(path.read_text(encoding="utf-8"))
    return "\n".join(contents)


def main() -> int:
    found, failures = definitions()
    for identifier, (document, line_number, references) in found.items():
        kind = identifier.split("-", 1)[0]
        expected_parent = EXPECTED_PARENT.get(kind)
        if expected_parent is None:
            continue
        parents = {
            reference
            for reference in references
            if reference.startswith(expected_parent + "-")
        }
        if not parents:
            failures.append(
                f"{document.relative_to(ROOT)}:{line_number}: {identifier} から {expected_parent} への参照がありません"
            )
            continue
        for parent in parents:
            if parent not in found:
                failures.append(f"{identifier} が未定義の {parent} を参照しています")

    sources = test_sources()
    for identifier in found:
        if not identifier.startswith(("ST-", "IT-")):
            continue
        marker = identifier.replace("-", "")
        if re.search(re.escape(marker), sources, re.IGNORECASE) is None:
            failures.append(f"{identifier} に対応する実在テストがありません")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("要求からテストの対応: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
