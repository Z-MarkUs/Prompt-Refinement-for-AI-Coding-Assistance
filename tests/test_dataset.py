from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from prompt_refinement_eval.dataset import (
    BenchmarkCase,
    DatasetFormatError,
    FineTuningExample,
    FineTuningMessage,
    benchmark_fingerprint,
    load_benchmark,
    load_jsonl,
    validate_benchmark,
    validate_fine_tuning,
    validate_train_benchmark_overlaps,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _write_benchmark(path: Path, rows: list[list[str]], *, header: bool = False) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        if header:
            writer.writerow(["id", "difficulty", "description", "signature"])
        writer.writerows(rows)


def _conversation(
    line: int,
    *,
    user: str = "Explain the task.",
    assistant: str = '{"description": "A precise task"}',
) -> FineTuningExample:
    return FineTuningExample(
        messages=(
            FineTuningMessage("system", "Refine coding prompts."),
            FineTuningMessage("user", user),
            FineTuningMessage("assistant", assistant),
        ),
        source_line=line,
    )


def test_load_benchmark_handles_header_and_multiline_fields(tmp_path: Path) -> None:
    path = tmp_path / "benchmark.csv"
    signature = "class Solution:\n    def solve(self, value: int) -> int:\n        "
    _write_benchmark(
        path,
        [["17", "Easy", "Return the value.\nKeep it unchanged.", signature]],
        header=True,
    )

    cases = load_benchmark(path)

    assert len(cases) == 1
    assert cases[0].id == 17
    assert cases[0].source_line == 2
    assert cases[0].method_name == "solve"
    assert "\n" in cases[0].description
    assert validate_benchmark(cases).is_valid


def test_load_benchmark_rejects_malformed_row(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("1,Easy,missing signature\n", encoding="utf-8")

    with pytest.raises(DatasetFormatError, match="expected 4 CSV columns"):
        load_benchmark(path)


def test_validate_benchmark_reports_identity_and_signature_errors() -> None:
    cases = [
        BenchmarkCase(1, "Easy", "First", "class Solution:\n    def one(self):", 1),
        BenchmarkCase(1, "Unknown", "", "class Solution", 2),
    ]

    report = validate_benchmark(cases)
    codes = {issue.code for issue in report.issues}

    assert not report.is_valid
    assert report.error_count >= 4
    assert "benchmark.duplicate_task_id" in codes
    assert "benchmark.invalid_difficulty" in codes
    assert "benchmark.empty_description" in codes
    assert "benchmark.invalid_python_signature" in codes
    assert report.to_dict()["is_valid"] is False


def test_duplicate_signature_uses_description_to_surface_likely_mismatch() -> None:
    signature = "class Solution:\n    def countBoxes(self, boxes: List[int]) -> int:"
    cases = [
        BenchmarkCase(10, "Easy", "Count the boxes in the list of boxes.", signature, 1),
        BenchmarkCase(11, "Easy", "Return the richest customer's wealth.", signature, 2),
    ]

    report = validate_benchmark(cases)
    mismatch = [
        issue for issue in report.issues if issue.code == "benchmark.signature_description_mismatch"
    ]

    assert len(mismatch) == 1
    assert mismatch[0].record_ids == (11,)
    assert any(issue.code == "benchmark.duplicate_signature" for issue in report.issues)


def test_repository_benchmark_surfaces_known_mismatch_candidates() -> None:
    cases = load_benchmark(PROJECT_ROOT / "AutoTest" / "test.csv")

    report = validate_benchmark(cases)
    mismatch_ids = {
        issue.record_ids[0]
        for issue in report.issues
        if issue.code == "benchmark.signature_description_mismatch"
    }

    assert len(cases) == 200
    assert report.error_count == 0
    assert report.is_valid
    assert mismatch_ids == {1003, 1564, 1672}
    assert len(report.sha256) == 64


def test_repository_design_interfaces_are_valid_exactly_as_exported() -> None:
    design_ids = {1032, 1157, 1500, 1570, 1603, 1656}
    cases = [
        case
        for case in load_benchmark(PROJECT_ROOT / "AutoTest" / "test.csv")
        if case.task_id in design_ids
    ]

    report = validate_benchmark(cases)

    assert {case.task_id for case in cases} == design_ids
    assert report.is_valid
    assert all(case.method_name is None for case in cases)


def test_non_solution_interface_without_constructor_is_rejected() -> None:
    case = BenchmarkCase(
        1,
        "Easy",
        "Return indices of two values that add to a target.",
        "class Typo:\n    def twoSum(self, nums: list[int], target: int) -> list[int]:\n",
        1,
    )

    report = validate_benchmark([case])

    assert not report.is_valid
    assert "benchmark.design_interface_constructor" in {issue.code for issue in report.issues}


def test_curated_manifest_is_tied_to_raw_benchmark_and_covers_findings() -> None:
    cases = load_benchmark(PROJECT_ROOT / "AutoTest" / "test.csv")
    report = validate_benchmark(cases)
    manifest = json.loads(
        (PROJECT_ROOT / "data" / "curated" / "benchmark_corrections.json").read_text(
            encoding="utf-8"
        )
    )
    corrections = {item["task_id"]: item for item in manifest["corrections"]}

    assert manifest["source_content_sha256"] == report.sha256
    assert set(corrections) == {1003, 1564, 1672}
    assert corrections[1003]["corrected_method"] == "isValid"
    assert corrections[1564]["action"] == "replace_description"
    assert (
        corrections[1564]["original_signature"]
        == corrections[1564]["corrected_canonical_signature"]
    )
    assert corrections[1672]["corrected_method"] == "maximumWealth"


def test_benchmark_fingerprint_is_stable_and_content_sensitive() -> None:
    original = [BenchmarkCase(1, "Easy", "Return one.", "class Solution:\n    def one(self):", 4)]
    moved_line = [
        BenchmarkCase(1, "Easy", "Return one.", "class Solution:\n    def one(self):", 99)
    ]
    changed = [BenchmarkCase(1, "Easy", "Return two.", "class Solution:\n    def one(self):", 4)]

    assert benchmark_fingerprint(original) == benchmark_fingerprint(moved_line)
    assert benchmark_fingerprint(original) != benchmark_fingerprint(changed)


def test_load_and_validate_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "training.jsonl"
    record = {
        "messages": [
            {"role": "system", "content": "Refine coding prompts."},
            {"role": "user", "content": "Explain the task."},
            {"role": "assistant", "content": '{"description": "Precise"}'},
        ]
    }
    path.write_text(f"{json.dumps(record)}\n", encoding="utf-8")

    examples = load_jsonl(path)
    report = validate_fine_tuning(examples)

    assert examples[0].messages[1].role == "user"
    assert report.is_valid
    assert report.record_count == 1


@pytest.mark.parametrize(
    ("content", "expected_code"),
    [
        ("not-json", "fine_tuning.assistant_content_not_json"),
        ("[]", "fine_tuning.assistant_content_not_object"),
        ("{}", "fine_tuning.empty_assistant_object"),
    ],
)
def test_validate_fine_tuning_rejects_unusable_assistant_content(
    content: str, expected_code: str
) -> None:
    report = validate_fine_tuning([_conversation(1, assistant=content)])

    assert not report.is_valid
    assert report.issues[0].code == expected_code


def test_repository_training_export_surfaces_empty_assistant_object() -> None:
    report = validate_fine_tuning(load_jsonl(PROJECT_ROOT / "Model Fine-Tuning" / "train.jsonl"))

    findings = [
        issue for issue in report.issues if issue.code == "fine_tuning.empty_assistant_object"
    ]
    assert len(findings) == 1
    assert findings[0].line_numbers == (271,)


def test_repository_overlap_manifest_is_hash_bound_and_emits_two_warnings() -> None:
    report = validate_train_benchmark_overlaps(
        load_benchmark(PROJECT_ROOT / "AutoTest" / "test.csv"),
        load_jsonl(PROJECT_ROOT / "Model Fine-Tuning" / "train.jsonl"),
        PROJECT_ROOT / "data" / "curated" / "train_benchmark_overlaps.json",
    )

    overlaps = [
        issue for issue in report.issues if issue.code == "cross_dataset.confirmed_task_overlap"
    ]
    assert report.is_valid
    assert report.record_count == 2
    assert report.error_count == 0
    assert {issue.record_ids[0] for issue in overlaps} == {1009, 1038}


def test_exact_train_benchmark_text_match_is_a_hard_error(tmp_path: Path) -> None:
    cases = [
        BenchmarkCase(
            1,
            "Easy",
            "Return one value!",
            "class Solution:\n    def one(self):",
            1,
        )
    ]
    examples = [_conversation(1, user="  RETURN one value  ")]
    manifest = tmp_path / "overlaps.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "normalization": "nfkc-casefold-ascii-alnum-v1",
                "sources": {
                    "benchmark": {
                        "record_count": 1,
                        "content_sha256": benchmark_fingerprint(cases),
                    },
                    "train": {
                        "record_count": 1,
                        "content_sha256": validate_fine_tuning(examples).sha256,
                    },
                },
                "confirmed_overlaps": [],
                "reviewed_non_overlaps": [],
            }
        ),
        encoding="utf-8",
    )

    report = validate_train_benchmark_overlaps(cases, examples, manifest)

    assert not report.is_valid
    assert "cross_dataset.exact_text_overlap" in {issue.code for issue in report.issues}


def test_validate_fine_tuning_reports_duplicates_and_role_sequence() -> None:
    duplicated = _conversation(1)
    wrong_roles = FineTuningExample(
        messages=(
            FineTuningMessage("user", "Explain the task."),
            FineTuningMessage("assistant", '{"description": "A precise task"}'),
            FineTuningMessage("system", "Refine coding prompts."),
        ),
        source_line=2,
    )

    report = validate_fine_tuning([duplicated, duplicated, wrong_roles])
    codes = {issue.code for issue in report.issues}

    assert "fine_tuning.duplicate_conversation" in codes
    assert "fine_tuning.duplicate_user_prompt" in codes
    assert "fine_tuning.unexpected_role_sequence" in codes


def test_load_jsonl_surfaces_line_number_for_structural_failure(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text('{"messages": []}\n{"messages": "wrong"}\n', encoding="utf-8")

    with pytest.raises(DatasetFormatError) as captured:
        load_jsonl(path)

    assert captured.value.line_number == 2
