from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from prompt_refinement_eval.cli import main


def _write_benchmark(path: Path, *, valid: bool = True) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "1",
                "Easy",
                "Return one.",
                "class Solution:\n    def one(self) -> int:\n        ",
            ]
            if valid
            else ["1", "Unknown", "", "not python"],
        )


def _write_jsonl(path: Path) -> None:
    record = {
        "messages": [
            {"role": "system", "content": "Refine the task."},
            {"role": "user", "content": "Return one."},
            {"role": "assistant", "content": json.dumps({"objective": "Return one."})},
        ]
    }
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")


def _write_arm(path: Path, status: str) -> None:
    accepted = status == "Accepted"
    path.write_text(
        json.dumps(
            {
                "total": 1,
                "success": int(accepted),
                "failed": int(not accepted),
                "detail": {"1": {"status_msg": status}},
            }
        ),
        encoding="utf-8",
    )


def test_validate_writes_machine_readable_result(tmp_path: Path) -> None:
    benchmark = tmp_path / "benchmark.csv"
    train = tmp_path / "train.jsonl"
    validation = tmp_path / "validation.jsonl"
    output = tmp_path / "reports" / "validation.json"
    _write_benchmark(benchmark)
    _write_jsonl(train)
    _write_jsonl(validation)

    status = main(
        [
            "validate",
            "--benchmark",
            str(benchmark),
            "--train",
            str(train),
            "--validation",
            str(validation),
            "--output",
            str(output),
        ]
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert status == 0
    assert payload["is_valid"] is True
    assert payload["benchmark"]["record_count"] == 1
    assert len(payload["benchmark"]["sha256"]) == 64
    assert payload["cross_dataset"] is None


def test_validate_returns_one_for_invalid_dataset(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    benchmark = tmp_path / "benchmark.csv"
    train = tmp_path / "train.jsonl"
    validation = tmp_path / "validation.jsonl"
    _write_benchmark(benchmark, valid=False)
    _write_jsonl(train)
    _write_jsonl(validation)

    status = main(
        [
            "validate",
            "--benchmark",
            str(benchmark),
            "--train",
            str(train),
            "--validation",
            str(validation),
        ]
    )

    assert status == 1
    assert json.loads(capsys.readouterr().out)["is_valid"] is False


def test_analyze_and_report_create_reproducible_artifacts(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    refined = tmp_path / "refined.json"
    analysis = tmp_path / "out" / "analysis.json"
    markdown = tmp_path / "out" / "results.md"
    report_json = tmp_path / "out" / "report-analysis.json"
    _write_arm(baseline, "Accepted")
    _write_arm(refined, "Wrong Answer")
    arms = [
        "--arm",
        f"baseline_gpt35={baseline}",
        "--arm",
        f"finetuned_refiner_gpt35={refined}",
    ]

    analyze_status = main(["analyze", *arms, "--output", str(analysis)])
    report_status = main(
        [
            "report",
            *arms,
            "--output",
            str(markdown),
            "--analysis-output",
            str(report_json),
        ]
    )

    assert analyze_status == report_status == 0
    assert json.loads(analysis.read_text(encoding="utf-8"))["task_union"]["task_count"] == 1
    assert json.loads(report_json.read_text(encoding="utf-8"))["pairwise"][0]["paired_count"] == 1
    assert "does not demonstrate an improvement" in markdown.read_text(encoding="utf-8")


def test_duplicate_arm_and_missing_file_return_clean_errors(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    arm = tmp_path / "arm.json"
    _write_arm(arm, "Accepted")

    duplicate_status = main(["analyze", "--arm", f"same={arm}", "--arm", f"same={arm}"])
    missing_status = main(
        [
            "analyze",
            "--arm",
            f"first={tmp_path / 'missing.json'}",
            "--arm",
            f"second={arm}",
        ]
    )

    errors = capsys.readouterr().err
    assert duplicate_status == missing_status == 2
    assert "duplicate arm name" in errors
    assert "missing.json" in errors


def test_default_arms_explain_repository_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.chdir(tmp_path)

    status = main(["analyze"])

    assert status == 2
    error = capsys.readouterr().err
    assert "run from the repository root" in error
    assert "--arm NAME=PATH" in error


def test_invalid_arm_syntax_is_rejected_by_argparse() -> None:
    with pytest.raises(SystemExit) as error:
        main(["analyze", "--arm", "missing-separator"])
    assert error.value.code == 2
