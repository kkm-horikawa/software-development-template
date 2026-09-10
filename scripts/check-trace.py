#!/usr/bin/env python3
"""課題からIssue単位のテストまでの参照と番号を検算する。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRECTORIES = {".git", ".pytest_cache", ".venv", "__pycache__"}
LONG_LIVED = r"(?:PB|SC|REQ|AC)-\d{3}"
INCREMENT_LOCAL = r"(?:SPEC|ST|AD|IT)-\d+(?:-\d+)*-\d{2}"
IDENTIFIER = rf"(?:{LONG_LIVED}|{INCREMENT_LOCAL})"
DEFINITION = re.compile(rf"^#{{1,6}}\s+({IDENTIFIER})\b")
REFERENCE = re.compile(rf"\[({IDENTIFIER})\]")
LEGACY_INCREMENT_ID = re.compile(r"^#{1,6}\s+(?:SPEC|ST|AD|IT)-\d{3}\b")
ISSUE = re.compile(r"^対応Issue:\s*#(\d+)\s*$", re.MULTILINE)
EXPECTED_PARENT = {
    "SC": "PB",
    "REQ": "SC",
    "AC": "REQ",
    "SPEC": "AC",
    "ST": "SPEC",
    "AD": "SPEC",
    "IT": "AD",
}


def requirement_documents() -> list[Path]:
    return [
        path
        for path in sorted((ROOT / "docs/110_requirements").rglob("*.md"))
        if path.name != "README.md"
    ]


def increment_documents() -> list[Path]:
    return sorted((ROOT / "docs/210_increments").glob("INC-*.md"))


def trace_documents() -> list[Path]:
    return [*requirement_documents(), *increment_documents()]


def definitions() -> tuple[dict[str, tuple[Path, int, set[str]]], list[str]]:
    found: dict[str, tuple[Path, int, set[str]]] = {}
    failures: list[str] = []
    for document in trace_documents():
        for line_number, line in enumerate(
            document.read_text(encoding="utf-8").splitlines(), 1
        ):
            if LEGACY_INCREMENT_ID.match(line):
                failures.append(
                    f"{document.relative_to(ROOT)}:{line_number}: 増分内の識別子にIssue番号がありません"
                )
            match = DEFINITION.match(line)
            if not match:
                continue
            identifier = match.group(1)
            if identifier in found:
                failures.append(f"{identifier} が二重に定義されています")
                continue
            found[identifier] = (document, line_number, set(REFERENCE.findall(line)))
    return found, failures


def validate_increment_numbers(
    found: dict[str, tuple[Path, int, set[str]]],
) -> list[str]:
    failures: list[str] = []
    for document in increment_documents():
        increment_key = document.stem.removeprefix("INC-")
        issue_number = increment_key.split("-", 1)[0]
        content = document.read_text(encoding="utf-8")
        issue = ISSUE.search(content)
        if issue is None or issue.group(1) != issue_number:
            failures.append(
                f"{document.relative_to(ROOT)}: ファイル名のIssue番号と対応Issueが一致しません"
            )
        local_ids = [
            identifier
            for identifier, (source, _line, _references) in found.items()
            if source == document
            and identifier.split("-", 1)[0] in {"SPEC", "ST", "AD", "IT"}
        ]
        if not local_ids:
            failures.append(f"{document.relative_to(ROOT)}: 増分内の識別子がありません")
        for identifier in local_ids:
            kind = identifier.split("-", 1)[0]
            if not identifier.startswith(f"{kind}-{increment_key}-"):
                failures.append(
                    f"{document.relative_to(ROOT)}: {identifier} が増分キー {increment_key} と一致しません"
                )
    return failures


def test_sources() -> str:
    contents: list[str] = []
    for pattern in ("**/test_*.py", "**/*_test.go"):
        for path in ROOT.glob(pattern):
            if not any(part in SKIP_DIRECTORIES for part in path.parts):
                contents.append(path.read_text(encoding="utf-8"))
    return "\n".join(contents)


def normalized(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]", "", value).lower()


def main() -> int:
    found, failures = definitions()
    failures.extend(validate_increment_numbers(found))
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

    sources = normalized(test_sources())
    for identifier in found:
        if not identifier.startswith(("ST-", "IT-")):
            continue
        if normalized(identifier) not in sources:
            failures.append(f"{identifier} に対応する実在テストがありません")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("要求からテストの対応: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
