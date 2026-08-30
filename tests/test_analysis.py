from __future__ import annotations

import json
from pathlib import Path

import pytest

from prompt_refinement_eval.analysis import (
    ResultFormatError,
    analyze_historical_results,
    benchmark_audit_from_validation,
    exact_mcnemar_p_value,
    load_historical_result,
    overlap_risk_audit_from_validation,
    write_report_json,
)
from prompt_refinement_eval.dataset import (
    load_benchmark,
    load_jsonl,
    validate_benchmark,
    validate_train_benchmark_overlaps,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _write_results(
    path: Path,
    statuses: dict[int, str],
    *,
    declared_total: int | None = None,
    declared_success: int | None = None,
    declared_failed: int | None = None,
) -> None:
    accepted = sum(status == "Accepted" for status in statuses.values())
    payload = {
        "total": len(statuses) if declared_total is None else declared_total,
        "success": accepted if declared_success is None else declared_success,
        "failed": len(statuses) - accepted if declared_failed is None else declared_failed,
        "detail": {
            str(task_id): {"status_msg": status, "status_code": 10 if status == "Accepted" else 11}
            for task_id, status in statuses.items()
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_analyze_historical_results_pairs_by_id_and_accounts_for_missingness(
    tmp_path: Path,
) -> None:
    baseline = tmp_path / "baseline.json"
    refined = tmp_path / "refined.json"
    third = tmp_path / "third.json"
    _write_results(baseline, {1: "Accepted", 2: "Wrong Answer", 3: "Runtime Error"})
    _write_results(refined, {1: "Accepted", 2: "Accepted", 4: "Wrong Answer"})
    _write_results(
        third,
        {1: "Wrong Answer", 2: "Accepted", 3: "Accepted", 4: "Accepted"},
    )

    report = analyze_historical_results({"baseline": baseline, "refined": refined, "third": third})

    assert report.task_union_ids == (1, 2, 3, 4)
    assert all("\\" not in arm.source for arm in report.arms)
    assert report.complete_cases.task_ids == (1, 2)
    summaries = {arm.name: arm for arm in report.arms}
    assert summaries["baseline"].missing_ids == (4,)
    assert summaries["baseline"].failure_distribution == {
        "Runtime Error": 1,
        "Wrong Answer": 1,
    }
    archival_run = summaries["baseline"].archival_run
    assert archival_run.run_id == f"historical-{summaries['baseline'].source_sha256[:12]}"
    assert archival_run.strategy == "baseline"
    assert archival_run.generator_label == "not recorded"
    assert archival_run.refiner_label == "not recorded"
    assert summaries["baseline"].to_dict()["archival_run"] == archival_run.to_dict()

    comparison = next(
        item for item in report.pairwise if item.arm_a == "baseline" and item.arm_b == "refined"
    )
    assert comparison.paired_ids == (1, 2)
    assert comparison.only_a_ids == (3,)
    assert comparison.only_b_ids == (4,)
    assert comparison.both_accepted == 1
    assert comparison.b_only_accepted == 1
    assert comparison.arm_a_acceptance_rate == 0.5
    assert comparison.arm_b_acceptance_rate == 1.0
    assert comparison.acceptance_rate_difference_b_minus_a == 0.5
    assert comparison.mcnemar_exact_p_value == 1.0


def test_exact_mcnemar_p_value_matches_known_binomial_tail() -> None:
    assert exact_mcnemar_p_value(1, 9) == pytest.approx(0.021484375)
    assert exact_mcnemar_p_value(0, 0) == 1.0
    assert exact_mcnemar_p_value(4, 4) == 1.0
    with pytest.raises(ValueError, match="non-negative"):
        exact_mcnemar_p_value(-1, 2)


def test_loader_records_declared_count_and_missing_status_issues(tmp_path: Path) -> None:
    path = tmp_path / "arm.json"
    path.write_text(
        json.dumps(
            {
                "total": 99,
                "success": 1,
                "failed": 0,
                "detail": {"1": {"status_code": 11}},
            }
        ),
        encoding="utf-8",
    )

    arm = load_historical_result(path, "arm")
    codes = [issue.code for issue in arm.issues]

    assert arm.records[1].status == "Unknown"
    assert "result.missing_status" in codes
    assert "result.declared_count_mismatch" in codes
    assert len(arm.source_sha256) == 64


def test_result_and_manifest_fingerprints_ignore_checkout_newlines(tmp_path: Path) -> None:
    result_payload = json.dumps(
        {
            "total": 1,
            "success": 1,
            "failed": 0,
            "detail": {"1": {"status_msg": "Accepted"}},
        },
        indent=2,
    )
    result_lf = tmp_path / "result-lf.json"
    result_crlf = tmp_path / "result-crlf.json"
    result_lf.write_bytes(f"{result_payload}\n".encode())
    result_crlf.write_bytes(b"\xef\xbb\xbf" + f"{result_payload}\n".replace("\n", "\r\n").encode())

    assert (
        load_historical_result(result_lf).source_sha256
        == load_historical_result(result_crlf).source_sha256
    )

    cases = load_benchmark(PROJECT_ROOT / "AutoTest" / "test.csv")
    validation = validate_benchmark(cases)
    source_manifest = (
        PROJECT_ROOT / "data" / "curated" / "benchmark_corrections.json"
    ).read_bytes()
    canonical_manifest = source_manifest.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    manifest_lf = tmp_path / "corrections-lf.json"
    manifest_crlf = tmp_path / "corrections-crlf.json"
    manifest_lf.write_bytes(canonical_manifest)
    manifest_crlf.write_bytes(canonical_manifest.replace(b"\n", b"\r\n"))

    audit_lf = benchmark_audit_from_validation(
        validation,
        source=PROJECT_ROOT / "AutoTest" / "test.csv",
        task_ids=[case.task_id for case in cases],
        correction_manifest=manifest_lf,
    )
    audit_crlf = benchmark_audit_from_validation(
        validation,
        source=PROJECT_ROOT / "AutoTest" / "test.csv",
        task_ids=[case.task_id for case in cases],
        correction_manifest=manifest_crlf,
    )
    assert audit_lf.correction_manifest_sha256 == audit_crlf.correction_manifest_sha256


@pytest.mark.parametrize(
    "payload",
    ["[]", '{"detail": []}', '{"detail": {"not-an-id": {}}}'],
)
def test_loader_rejects_unusable_result_shapes(tmp_path: Path, payload: str) -> None:
    path = tmp_path / "bad.json"
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(ResultFormatError):
        load_historical_result(path)


@pytest.mark.parametrize(
    "payload",
    [
        '{"total": 2, "success": 2, "failed": 0, "detail": '
        '{"1": {"status_msg": "Accepted"}, "01": {"status_msg": "Accepted"}}}',
        '{"total": 1, "success": 1, "failed": 0, "detail": '
        '{"1": {"status_msg": "Accepted"}, "1": {"status_msg": "Accepted"}}}',
    ],
)
def test_loader_rejects_ambiguous_or_duplicate_task_keys(tmp_path: Path, payload: str) -> None:
    path = tmp_path / "ambiguous.json"
    path.write_text(payload, encoding="utf-8")

    with pytest.raises(ResultFormatError):
        load_historical_result(path)


def test_analysis_rejects_pair_with_no_shared_task_ids(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    _write_results(first, {1: "Accepted"})
    _write_results(second, {2: "Accepted"})

    with pytest.raises(ValueError, match="no shared task IDs"):
        analyze_historical_results({"first": first, "second": second})


def test_write_report_json_round_trips_serializable_report(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    output = tmp_path / "nested" / "report.json"
    _write_results(first, {1: "Accepted"})
    _write_results(second, {1: "Wrong Answer"})
    report = analyze_historical_results({"first": first, "second": second})

    write_report_json(report, output)
    saved = json.loads(output.read_text(encoding="utf-8"))

    assert saved["schema_version"] == "1.3"
    assert saved["arms"]["first"]["source_sha256_policy"].endswith("sha256-v1")
    assert saved["task_union"]["task_count"] == 1
    assert saved["pairwise"][0]["mcnemar"]["p_value"] == 1.0
    archival = saved["arms"]["first"]["archival_run"]
    assert archival["run_id"].startswith("historical-")
    assert archival["run_id_source"] == "derived_from_source_sha256"
    assert archival["model_labels"]["generator"] == "not recorded"
    assert archival["generation_parameters"]["recorded"] is False
    assert output.read_bytes().endswith(b"\n")


def test_repository_historical_results_are_reproduced_from_raw_artifacts() -> None:
    summary = PROJECT_ROOT / "AutoTest" / "leetcode_summary"
    benchmark_path = PROJECT_ROOT / "AutoTest" / "test.csv"
    benchmark_cases = load_benchmark(benchmark_path)
    benchmark_audit = benchmark_audit_from_validation(
        validate_benchmark(benchmark_cases),
        source=benchmark_path,
        task_ids=[case.task_id for case in benchmark_cases],
    )
    overlap_path = PROJECT_ROOT / "data" / "curated" / "train_benchmark_overlaps.json"
    overlap_validation = validate_train_benchmark_overlaps(
        benchmark_cases,
        load_jsonl(PROJECT_ROOT / "Model Fine-Tuning" / "train.jsonl"),
        overlap_path,
    )
    overlap_audit = overlap_risk_audit_from_validation(
        overlap_validation,
        source=overlap_path,
    )
    report = analyze_historical_results(
        {
            "baseline_gpt35": summary / "3.5_score_readable.json",
            "finetuned_refiner_gpt35": summary / "finetuned_score_readable.json",
            "gpt4o_refiner_gpt35": summary / "4o_3.5_score_readable.json",
        },
        benchmark_audit=benchmark_audit,
        overlap_risk_audit=overlap_audit,
    )
    arms = {arm.name: arm for arm in report.arms}

    assert (arms["baseline_gpt35"].accepted, arms["baseline_gpt35"].observed_total) == (
        134,
        197,
    )
    assert (
        arms["finetuned_refiner_gpt35"].accepted,
        arms["finetuned_refiner_gpt35"].observed_total,
    ) == (126, 196)
    assert (
        arms["gpt4o_refiner_gpt35"].accepted,
        arms["gpt4o_refiner_gpt35"].observed_total,
    ) == (55, 199)
    assert len(report.task_union_ids) == 200
    assert len(report.complete_cases.task_ids) == 193
    assert report.benchmark_alignment is not None
    assert report.benchmark_alignment.to_dict()["is_aligned"] is True
    assert report.sensitivity is not None
    assert report.sensitivity.excluded_task_ids == (1003, 1564, 1672)
    assert len(report.sensitivity.complete_case_ids) == 190
    assert report.overlap_risk_audit is not None
    assert report.overlap_risk_audit.confirmed_task_ids == (1009, 1038)
    assert report.overlap_risk_sensitivity is not None
    overlap_pair = next(
        comparison
        for comparison in report.overlap_risk_sensitivity.pairwise
        if comparison.arm_a == "baseline_gpt35" and comparison.arm_b == "finetuned_refiner_gpt35"
    )
    assert overlap_pair.paired_count == 192
    assert overlap_pair.arm_a_accepted == 130
    assert overlap_pair.arm_b_accepted == 123
    assert overlap_pair.a_only_accepted == 23
    assert overlap_pair.b_only_accepted == 16
    assert overlap_pair.acceptance_rate_difference_b_minus_a == pytest.approx(-7 / 192)
    assert overlap_pair.mcnemar_exact_p_value == pytest.approx(0.3367836351899314)
    assert not report.issues
