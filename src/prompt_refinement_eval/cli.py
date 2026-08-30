"""Command-line interface for offline validation and historical analysis."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from prompt_refinement_eval import __version__
from prompt_refinement_eval.analysis import (
    AnalysisReport,
    ResultFormatError,
    analyze_historical_results,
    benchmark_audit_from_validation,
    write_report_json,
)
from prompt_refinement_eval.dataset import (
    DatasetFormatError,
    load_benchmark,
    load_jsonl,
    validate_benchmark,
    validate_fine_tuning,
    validate_train_benchmark_overlaps,
)
from prompt_refinement_eval.reporting import render_markdown

DEFAULT_BENCHMARK = Path("AutoTest/test.csv")
DEFAULT_TRAIN = Path("Model Fine-Tuning/train.jsonl")
DEFAULT_VALIDATION = Path("Model Fine-Tuning/validation.jsonl")
DEFAULT_CORRECTION_MANIFEST = Path("data/curated/benchmark_corrections.json")
DEFAULT_OVERLAP_MANIFEST = Path("data/curated/train_benchmark_overlaps.json")
DEFAULT_ARMS = {
    "baseline_gpt35": Path("AutoTest/leetcode_summary/3.5_score_readable.json"),
    "finetuned_refiner_gpt35": Path("AutoTest/leetcode_summary/finetuned_score_readable.json"),
    "gpt4o_refiner_gpt35": Path("AutoTest/leetcode_summary/4o_3.5_score_readable.json"),
}


def build_parser() -> argparse.ArgumentParser:
    """Create the public CLI parser."""

    parser = argparse.ArgumentParser(
        prog="prompt-refinement-eval",
        description=(
            "Validate prompt-refinement datasets and reproduce paired historical analysis."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate", help="validate the benchmark and fine-tuning JSONL files"
    )
    validate_parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    validate_parser.add_argument("--train", type=Path, default=DEFAULT_TRAIN)
    validate_parser.add_argument("--validation", type=Path, default=DEFAULT_VALIDATION)
    validate_parser.add_argument(
        "--overlap-manifest",
        type=Path,
        help=(
            "curated train/benchmark overlap decisions "
            "(auto-detected only for the repository defaults)"
        ),
    )
    validate_parser.add_argument("--output", type=Path, help="write JSON instead of stdout")
    validate_parser.add_argument(
        "--strict-warnings",
        action="store_true",
        help="return a non-zero status when any warning is found",
    )

    analyze_parser = subparsers.add_parser(
        "analyze", help="reproduce ID-keyed historical comparisons"
    )
    _add_arm_arguments(analyze_parser)
    _add_benchmark_audit_argument(analyze_parser)
    analyze_parser.add_argument("--output", type=Path, help="write JSON instead of stdout")

    report_parser = subparsers.add_parser(
        "report", help="render an evidence-led Markdown results report"
    )
    _add_arm_arguments(report_parser)
    _add_benchmark_audit_argument(report_parser)
    report_parser.add_argument("--output", type=Path, help="write Markdown instead of stdout")
    report_parser.add_argument(
        "--analysis-output",
        type=Path,
        help="also write the machine-readable analysis JSON",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command and return a process status suitable for tests and CI."""

    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            return _run_validate(args)
        if args.command == "analyze":
            return _run_analyze(args)
        if args.command == "report":
            return _run_report(args)
    except (DatasetFormatError, ResultFormatError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    parser.error(f"unknown command: {args.command}")
    return 2


def _add_arm_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--arm",
        action="append",
        type=_parse_arm,
        metavar="NAME=PATH",
        help="result artifact to compare; repeat for each arm (defaults to repository artifacts)",
    )


def _add_benchmark_audit_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--benchmark",
        type=Path,
        help=(
            "benchmark used for provenance and identity-conflict sensitivity "
            "(auto-detected in a repository checkout)"
        ),
    )
    parser.add_argument(
        "--correction-manifest",
        type=Path,
        help="optional correction manifest bound to the benchmark fingerprint",
    )


def _parse_arm(value: str) -> tuple[str, Path]:
    name, separator, raw_path = value.partition("=")
    if not separator or not name.strip() or not raw_path.strip():
        raise argparse.ArgumentTypeError("arm must use NAME=PATH with non-empty values")
    return name.strip(), Path(raw_path.strip())


def _arm_paths(values: list[tuple[str, Path]] | None) -> dict[str, Path]:
    if values is None:
        missing = [path for path in DEFAULT_ARMS.values() if not path.is_file()]
        if missing:
            raise ValueError(
                "default historical artifacts were not found; run from the repository "
                "root or pass --arm NAME=PATH at least twice"
            )
        return dict(DEFAULT_ARMS)
    arms: dict[str, Path] = {}
    for name, path in values:
        if name in arms:
            raise ValueError(f"duplicate arm name: {name}")
        arms[name] = path
    if len(arms) < 2:
        raise ValueError("at least two --arm values are required")
    return arms


def _run_validate(args: argparse.Namespace) -> int:
    benchmark_cases = load_benchmark(args.benchmark)
    train_examples = load_jsonl(args.train)
    validation_examples = load_jsonl(args.validation)
    benchmark = validate_benchmark(benchmark_cases)
    train = validate_fine_tuning(train_examples)
    validation = validate_fine_tuning(validation_examples)
    overlap_manifest = args.overlap_manifest
    if (
        overlap_manifest is None
        and args.benchmark == DEFAULT_BENCHMARK
        and args.train == DEFAULT_TRAIN
        and DEFAULT_OVERLAP_MANIFEST.is_file()
    ):
        overlap_manifest = DEFAULT_OVERLAP_MANIFEST
    cross_dataset = (
        validate_train_benchmark_overlaps(benchmark_cases, train_examples, overlap_manifest)
        if overlap_manifest is not None
        else None
    )
    reports = (benchmark, train, validation) + (
        (cross_dataset,) if cross_dataset is not None else ()
    )
    payload: dict[str, object] = {
        "schema_version": "1.1",
        "is_valid": all(report.is_valid for report in reports),
        "benchmark": benchmark.to_dict(),
        "fine_tuning": {
            "train": train.to_dict(),
            "validation": validation.to_dict(),
        },
        "cross_dataset": (
            {"train_benchmark": cross_dataset.to_dict()} if cross_dataset is not None else None
        ),
    }
    _emit_json(payload, args.output)
    has_warnings = any(report.warning_count for report in reports)
    if not payload["is_valid"] or (args.strict_warnings and has_warnings):
        return 1
    return 0


def _run_analyze(args: argparse.Namespace) -> int:
    report = _analysis_from_args(args)
    if args.output is None:
        _emit_json(report.to_dict(), None)
    else:
        write_report_json(report, args.output)
    return 0


def _run_report(args: argparse.Namespace) -> int:
    report = _analysis_from_args(args)
    markdown = render_markdown(report)
    if args.output is None:
        print(markdown, end="")
    else:
        _write_text(args.output, markdown)
    if args.analysis_output is not None:
        write_report_json(report, args.analysis_output)
    return 0


def _analysis_from_args(args: argparse.Namespace) -> AnalysisReport:
    benchmark_path = args.benchmark
    if benchmark_path is None and args.arm is None and DEFAULT_BENCHMARK.is_file():
        benchmark_path = DEFAULT_BENCHMARK
    benchmark_audit = None
    if benchmark_path is not None:
        benchmark_cases = load_benchmark(benchmark_path)
        validation = validate_benchmark(benchmark_cases)
        correction_manifest = args.correction_manifest
        if (
            correction_manifest is None
            and benchmark_path == DEFAULT_BENCHMARK
            and DEFAULT_CORRECTION_MANIFEST.is_file()
        ):
            correction_manifest = DEFAULT_CORRECTION_MANIFEST
        benchmark_audit = benchmark_audit_from_validation(
            validation,
            source=benchmark_path,
            task_ids=[case.task_id for case in benchmark_cases],
            correction_manifest=correction_manifest,
        )
    return analyze_historical_results(
        _arm_paths(args.arm),
        benchmark_audit=benchmark_audit,
    )


def _emit_json(payload: object, output: Path | None) -> None:
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if output is None:
        print(serialized, end="")
    else:
        _write_text(output, serialized)


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


if __name__ == "__main__":  # pragma: no cover - exercised by the console entry point
    raise SystemExit(main())
