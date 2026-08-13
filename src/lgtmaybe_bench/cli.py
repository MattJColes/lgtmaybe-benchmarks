"""Command-line interface for benchmark execution and report regeneration."""

from __future__ import annotations

import argparse
import shutil
import subprocess
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
    run.add_argument("--lgtmaybe", help=argparse.SUPPRESS)
    subparsers.add_parser("report", help="regenerate Markdown from stored raw results")
    return parser


def _positive(parser: argparse.ArgumentParser, name: str, value: int) -> None:
    if value < 1:
        parser.error(f"{name} must be at least 1")


def resolve_lgtmaybe_command(requested: str | None) -> list[str]:
    if requested is not None:
        executable = shutil.which(requested)
        if executable is None:
            raise ValueError(f"lgtmaybe executable not found: {requested}")
        return [executable]

    uv = shutil.which("uv")
    if uv is None:
        raise ValueError("uv executable not found; uv is required to install lgtmaybe")

    command = [uv, "tool", "run", "lgtmaybe@latest"]
    try:
        preflight = subprocess.run(
            [
                uv,
                "tool",
                "run",
                "--refresh-package",
                "lgtmaybe",
                "lgtmaybe@latest",
                "--version",
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("could not install the latest lgtmaybe release") from exc
    if preflight.returncode != 0:
        raise ValueError("could not install the latest lgtmaybe release")
    return command


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
        try:
            executable = resolve_lgtmaybe_command(args.lgtmaybe)
        except ValueError as exc:
            parser.error(str(exc))
        from lgtmaybe_bench.runner import execute_benchmark

        execute_benchmark(root, args, executable)
    except (OSError, ValueError) as exc:
        print(f"bench: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
