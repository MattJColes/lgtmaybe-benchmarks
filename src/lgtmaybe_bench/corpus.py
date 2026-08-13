"""Corpus discovery and validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lgtmaybe_bench.scoring import CaseTruth, parse_case

LENSES = {
    "security",
    "correctness",
    "performance",
    "complexity",
    "tests",
    "documentation",
    "deprecation",
    "intent",
    "ponytail",
    "spec",
}


@dataclass(frozen=True, slots=True)
class CorpusCase:
    path: Path
    truth: CaseTruth
    raw: dict[str, Any]


def discover_cases(root: Path, *, require_coverage: bool = False) -> list[CorpusCase]:
    """Load cases and validate every referenced changed-tree location."""
    if not root.is_dir():
        raise ValueError(f"corpus directory not found: {root}")
    cases: list[CorpusCase] = []
    for metadata in sorted(root.glob("*/case.json")):
        raw = json.loads(metadata.read_text(encoding="utf-8"))
        truth = parse_case(raw)
        if truth.name != metadata.parent.name:
            raise ValueError(
                f"case name {truth.name!r} must match directory {metadata.parent.name!r}"
            )
        for entry in (*truth.expected, *truth.forbidden):
            if entry.lens not in LENSES:
                raise ValueError(f"{truth.name}: invalid lens {entry.lens!r}")
            source = metadata.parent / "changed" / entry.file
            if not source.is_file():
                raise ValueError(f"{truth.name}: missing changed file {entry.file}")
            line_count = len(source.read_text(encoding="utf-8").splitlines())
            if entry.line > line_count:
                raise ValueError(f"{truth.name}: line {entry.line} is outside {entry.file}")
        if not (metadata.parent / "base").is_dir():
            raise ValueError(f"{truth.name}: missing base tree")
        cases.append(CorpusCase(metadata.parent, truth, raw))
    if not cases:
        raise ValueError("corpus contains no cases")
    if require_coverage:
        counts = {lens: 0 for lens in LENSES}
        for case in cases:
            for entry in case.truth.expected:
                counts[entry.lens] += 1
        missing = [lens for lens, count in sorted(counts.items()) if count < 2]
        if missing:
            raise ValueError(
                f"corpus coverage needs two expected findings for: {', '.join(missing)}"
            )
        if not any(len({entry.file for entry in case.truth.expected}) > 1 for case in cases):
            raise ValueError("corpus coverage requires a multi-file case")
    return cases


def select_cases(cases: list[CorpusCase], names: list[str] | None) -> list[CorpusCase]:
    if not names:
        return cases
    by_name = {case.truth.name: case for case in cases}
    unknown = [name for name in names if name not in by_name]
    if unknown:
        raise ValueError(f"unknown case(s): {', '.join(unknown)}")
    return [by_name[name] for name in names]
