#!/usr/bin/env python3
"""課題から現在の受入例とIssue単位の検査までの参照を検算する。"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "docs/110_requirements"
SCENARIOS = REQUIREMENTS / "シナリオ"
INCREMENTS = ROOT / "docs/210_increments"
LONG_LIVED = r"(?:PB|SC|REQ)-\d{3}"
ACCEPTANCE = r"AC-SC\d{3}-\d{2}"
EXAMPLE = r"EX-SC\d{3}-\d{2}"
INCREMENT_LOCAL = r"(?:SPEC|ST|AD|IT)-\d+(?:-\d+)*-\d{2}"
IDENTIFIER = rf"(?:{LONG_LIVED}|{ACCEPTANCE}|{EXAMPLE}|{INCREMENT_LOCAL})"
DEFINITION = re.compile(rf"^#{{1,6}}\s+({IDENTIFIER})\b")
REFERENCE = re.compile(rf"\[({IDENTIFIER})\]")
LEGACY_INCREMENT_ID = re.compile(r"^#{1,6}\s+(?:SPEC|ST|AD|IT)-\d{3}\b")
ISSUE = re.compile(r"^対応Issue:\s*#(\d+)\s*$", re.MULTILINE)
TEST_REFERENCE = re.compile(
    r"`((?:backend|client|tests|scripts)/[^`]+::[A-Za-z0-9_-]+)`"
)
EXPECTED_PARENT = {
    "SC": "PB",
    "REQ": "SC",
    "AC": "REQ",
    "EX": "AC",
    "SPEC": "AC",
    "ST": "SPEC",
    "AD": "SPEC",
    "IT": "AD",
}


def requirement_documents() -> list[Path]:
    ignored = {
        REQUIREMENTS / "README.md",
        SCENARIOS / "README.md",
        SCENARIOS / "_template.md",
        SCENARIOS / "_acceptance-template.md",
    }
    return [path for path in sorted(REQUIREMENTS.rglob("*.md")) if path not in ignored]


def increment_documents() -> list[Path]:
    return sorted(INCREMENTS.glob("INC-*.md"))


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


def validate_scenario_numbers(
    found: dict[str, tuple[Path, int, set[str]]],
) -> list[str]:
    failures: list[str] = []
    for scenario in sorted(SCENARIOS.glob("SC-*")):
        if not scenario.is_dir():
            continue
        scenario_number = scenario.name.split("-", 2)[1]
        acceptance_key = f"SC{scenario_number}"
        acceptance_document = scenario / "受入例.md"
        local_ids = [
            identifier
            for identifier, (source, _line, _references) in found.items()
            if source == acceptance_document
            and identifier.split("-", 1)[0] in {"AC", "EX"}
        ]
        if not any(identifier.startswith("AC-") for identifier in local_ids):
            failures.append(
                f"{acceptance_document.relative_to(ROOT)}: 受入条件がありません"
            )
        if not any(identifier.startswith("EX-") for identifier in local_ids):
            failures.append(
                f"{acceptance_document.relative_to(ROOT)}: 具体例がありません"
            )
        for identifier in local_ids:
            kind = identifier.split("-", 1)[0]
            if not identifier.startswith(f"{kind}-{acceptance_key}-"):
                failures.append(
                    f"{acceptance_document.relative_to(ROOT)}: {identifier} が {scenario.name} と一致しません"
                )
    return failures


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


def section_test_references() -> dict[str, list[str]]:
    references: dict[str, list[str]] = {}
    for document in trace_documents():
        current: str | None = None
        for line in document.read_text(encoding="utf-8").splitlines():
            definition = DEFINITION.match(line)
            if definition:
                current = definition.group(1)
                references.setdefault(current, [])
                continue
            if current is not None:
                references[current].extend(TEST_REFERENCE.findall(line))
    return references


def validate_test_references(found: dict[str, tuple[Path, int, set[str]]]) -> list[str]:
    failures: list[str] = []
    references = section_test_references()
    for identifier in found:
        if identifier.split("-", 1)[0] not in {"EX", "ST", "IT"}:
            continue
        tests = references.get(identifier, [])
        if not tests:
            failures.append(f"{identifier} に実行物の参照がありません")
            continue
        for test in tests:
            path_text, test_name = test.split("::", 1)
            path = ROOT / path_text
            if not path.is_file():
                failures.append(
                    f"{identifier} が存在しないテストを参照しています: {path_text}"
                )
                continue
            if test_name not in path.read_text(encoding="utf-8"):
                failures.append(
                    f"{identifier} が存在しないテスト名を参照しています: {test}"
                )
    return failures


def main() -> int:
    found, failures = definitions()
    failures.extend(validate_scenario_numbers(found))
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

    failures.extend(validate_test_references(found))
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("要求から受入例とテストの対応: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
