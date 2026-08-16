"""One-shot builder for the long-horizon corpus suite.

Run with `uv run python scripts/generate_context_cases.py`. Generated cases are
immutable corpus artefacts; this script never runs as part of a benchmark.
"""

from __future__ import annotations

from pathlib import Path

from lgtmaybe_bench.context_generator import CASE_NAMES, SUITE_ID, generate_suite


def main() -> None:
    root = Path(__file__).resolve().parents[1] / "corpus"
    generate_suite(root)
    print(f"wrote {len(CASE_NAMES)} cases and suites/{SUITE_ID}.json under {root}")


if __name__ == "__main__":
    main()
