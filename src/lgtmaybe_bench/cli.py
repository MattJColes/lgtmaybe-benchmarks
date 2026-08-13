"""Command-line interface for benchmark execution and report regeneration."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

LOCAL_PROVIDERS = {"ollama", "openai-compatible"}


def resolved_concurrency(provider: str, requested: int | None) -> int:
    return requested if requested is not None else (1 if provider in LOCAL_PROVIDERS else 6)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bench", description="Benchmark lgtmaybe configurations")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="run lgtmaybe against the benchmark corpus")
    run.add_argument("--provider", required=True)
    run.add_argument("--model", required=True)
    run.add_argument("--reasoning-effort")
    run.add_argument("--max-tokens", type=int)
    run.add_argument("--max-input-tokens", type=int)
    run.add_argument("--preset", default="full", choices=("fast", "full"))
    run.add_argument("--repeats", type=int, default=3)
    run.add_argument("--case", action="append")
    run.add_argument("--api-base")
    run.add_argument("--concurrency", type=int)
    run.add_argument("--timeout", type=int, default=7200)
    run.add_argument("--lgtmaybe", default="lgtmaybe", help=argparse.SUPPRESS)
    subparsers.add_parser("report", help="regenerate Markdown from stored raw results")
    return parser


def _positive(parser: argparse.ArgumentParser, name: str, value: int) -> None:
    if value < 1:
        parser.error(f"{name} must be at least 1")


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path.cwd()
    try:
        if args.command == "report":
            from lgtmaybe_bench.reporting import regenerate_reports

            regenerate_reports(root)
            return
        _positive(parser, "--repeats", args.repeats)
        _positive(parser, "--timeout", args.timeout)
        if args.concurrency is not None:
            _positive(parser, "--concurrency", args.concurrency)
        executable = shutil.which(args.lgtmaybe)
        if executable is None:
            parser.error(f"lgtmaybe executable not found: {args.lgtmaybe}")
        from lgtmaybe_bench.runner import execute_benchmark

        execute_benchmark(root, args, executable)
    except (OSError, ValueError) as exc:
        print(f"bench: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
