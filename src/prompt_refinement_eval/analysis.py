"""Paired, ID-keyed analysis of the repository's historical judge results."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

from prompt_refinement_eval import __version__
from prompt_refinement_eval.dataset import DatasetValidation
from prompt_refinement_eval.fingerprints import (
    CANONICAL_JSON_SHA256_POLICY,
    CANONICAL_TEXT_SHA256_POLICY,
    canonical_text_sha256,
)

_SENSITIVITY_ISSUE_CODES = frozenset({"benchmark.signature_description_mismatch"})
_EMPTY_IDS: frozenset[int] = frozenset()
_CANONICAL_TASK_ID = re.compile(r"[1-9][0-9]*")


class _DuplicateJsonKey(ValueError):
    """Internal signal raised while decoding an object with repeated keys."""

    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(key)


class ResultFormatError(ValueError):
    """Raised when a historical result artifact has an unusable structure."""

    def __init__(self, path: Path, message: str) -> None:
        self.path = path
        self.problem = message
        super().__init__(f"{path}: {message}")


@dataclass(frozen=True, slots=True)
class ResultRecord:
    """The outcome for one benchmark task in one experiment arm."""

    task_id: int
    status: str
    accepted: bool
    task_finish_time_ms: int | None


@dataclass(frozen=True, slots=True)
class ReportIssue:
    """A provenance or summary-integrity issue found in a result artifact."""

    code: str
    arm: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "arm": self.arm, "message": self.message}


@dataclass(frozen=True, slots=True)
class HistoricalArm:
    """One loaded historical experiment arm before cross-arm analysis."""

    name: str
    source: Path
    source_sha256: str
    records: Mapping[int, ResultRecord]
    declared_total: int | None
    declared_success: int | None
    declared_failed: int | None
    issues: tuple[ReportIssue, ...]


@dataclass(frozen=True, slots=True)
class ArchivalRunMetadata:
    """Historical run labels separated from unsupported provider specifics."""

    run_id: str
    strategy: str
    generator_label: str
    refiner_label: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "run_id_source": "derived_from_source_sha256",
            "strategy": self.strategy,
            "model_labels": {
                "generator": self.generator_label,
                "refiner": self.refiner_label,
                "note": "historical labels; exact provider snapshots are not recorded",
            },
            "generation_parameters": {
                "recorded": False,
                "value": None,
                "note": "the result artifact does not bind exact inference parameters",
            },
        }


@dataclass(frozen=True, slots=True)
class ArmSummary:
    """Unpaired arm totals with explicit missingness against the task union."""

    name: str
    source: str
    source_sha256: str
    declared_total: int | None
    declared_success: int | None
    declared_failed: int | None
    observed_total: int
    accepted: int
    failed: int
    acceptance_rate: float | None
    failure_distribution: Mapping[str, int]
    missing_ids: tuple[int, ...]
    observed_run_started_at: str | None
    observed_run_ended_at: str | None
    archival_run: ArchivalRunMetadata

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "source": self.source,
            "source_sha256": self.source_sha256,
            "source_sha256_policy": CANONICAL_TEXT_SHA256_POLICY,
            "declared_total": self.declared_total,
            "declared_success": self.declared_success,
            "declared_failed": self.declared_failed,
            "observed_total": self.observed_total,
            "accepted": self.accepted,
            "failed": self.failed,
            "acceptance_rate": self.acceptance_rate,
            "failure_distribution": dict(self.failure_distribution),
            "missing_count": len(self.missing_ids),
            "missing_ids": list(self.missing_ids),
            "observed_judge_run_window": {
                "started_at": self.observed_run_started_at,
                "ended_at": self.observed_run_ended_at,
            },
            "archival_run": self.archival_run.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class CompleteCaseArm:
    """Performance for one arm on the all-arm task intersection."""

    name: str
    accepted: int
    failed: int
    acceptance_rate: float | None

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "accepted": self.accepted,
            "failed": self.failed,
            "acceptance_rate": self.acceptance_rate,
        }


@dataclass(frozen=True, slots=True)
class CompleteCaseSummary:
    """The intersection shared by every supplied experiment arm."""

    task_ids: tuple[int, ...]
    arms: tuple[CompleteCaseArm, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "task_count": len(self.task_ids),
            "task_ids": list(self.task_ids),
            "arms": {arm.name: arm.to_dict() for arm in self.arms},
        }


@dataclass(frozen=True, slots=True)
class PairwiseComparison:
    """A paired correctness comparison over the exact shared task IDs."""

    arm_a: str
    arm_b: str
    paired_ids: tuple[int, ...]
    only_a_ids: tuple[int, ...]
    only_b_ids: tuple[int, ...]
    both_accepted: int
    both_failed: int
    a_only_accepted: int
    b_only_accepted: int
    arm_a_accepted: int
    arm_b_accepted: int
    arm_a_acceptance_rate: float | None
    arm_b_acceptance_rate: float | None
    acceptance_rate_difference_b_minus_a: float | None
    mcnemar_exact_p_value: float

    @property
    def paired_count(self) -> int:
        return len(self.paired_ids)

    @property
    def ties(self) -> int:
        return self.both_accepted + self.both_failed

    @property
    def discordant_pairs(self) -> int:
        return self.a_only_accepted + self.b_only_accepted

    def to_dict(self) -> dict[str, object]:
        return {
            "arm_a": self.arm_a,
            "arm_b": self.arm_b,
            "paired_count": self.paired_count,
            "paired_ids": list(self.paired_ids),
            "missingness": {
                "only_a_count": len(self.only_a_ids),
                "only_a_ids": list(self.only_a_ids),
                "only_b_count": len(self.only_b_ids),
                "only_b_ids": list(self.only_b_ids),
            },
            "contingency": {
                "both_accepted": self.both_accepted,
                "both_failed": self.both_failed,
                "a_only_accepted": self.a_only_accepted,
                "b_only_accepted": self.b_only_accepted,
                "ties": self.ties,
                "discordant_pairs": self.discordant_pairs,
            },
            "arm_a_accepted": self.arm_a_accepted,
            "arm_b_accepted": self.arm_b_accepted,
            "arm_a_acceptance_rate": self.arm_a_acceptance_rate,
            "arm_b_acceptance_rate": self.arm_b_acceptance_rate,
            "acceptance_rate_difference_b_minus_a": (self.acceptance_rate_difference_b_minus_a),
            "mcnemar": {
                "test": "two-sided exact McNemar (binomial)",
                "p_value": self.mcnemar_exact_p_value,
            },
        }


@dataclass(frozen=True, slots=True)
class BenchmarkAuditSummary:
    """Benchmark provenance and validation findings relevant to interpretation."""

    source: str
    record_count: int
    sha256: str
    is_valid: bool
    error_count: int
    warning_count: int
    issue_codes: tuple[str, ...]
    validation_summary_sha256: str
    task_ids: tuple[int, ...]
    flagged_task_ids: tuple[int, ...]
    sensitivity_excluded_task_ids: tuple[int, ...]
    correction_manifest_source: str | None
    correction_manifest_sha256: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "record_count": self.record_count,
            "sha256": self.sha256,
            "sha256_policy": CANONICAL_JSON_SHA256_POLICY,
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issue_codes": list(self.issue_codes),
            "validation_summary_sha256": self.validation_summary_sha256,
            "validation_summary_sha256_policy": CANONICAL_JSON_SHA256_POLICY,
            "task_ids": list(self.task_ids),
            "flagged_task_ids": list(self.flagged_task_ids),
            "sensitivity_excluded_task_ids": list(self.sensitivity_excluded_task_ids),
            "correction_manifest": {
                "source": self.correction_manifest_source,
                "sha256": self.correction_manifest_sha256,
                "sha256_policy": CANONICAL_TEXT_SHA256_POLICY,
            },
        }


@dataclass(frozen=True, slots=True)
class SensitivitySummary:
    """Paired results after excluding task IDs for a documented audit reason."""

    reason: str
    excluded_task_ids: tuple[int, ...]
    retained_union_ids: tuple[int, ...]
    complete_case_ids: tuple[int, ...]
    complete_case_arms: tuple[CompleteCaseArm, ...]
    pairwise: tuple[PairwiseComparison, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "reason": self.reason,
            "excluded_task_ids": list(self.excluded_task_ids),
            "retained_union_count": len(self.retained_union_ids),
            "retained_union_ids": list(self.retained_union_ids),
            "complete_case_count": len(self.complete_case_ids),
            "complete_case_ids": list(self.complete_case_ids),
            "complete_case_arms": {arm.name: arm.to_dict() for arm in self.complete_case_arms},
            "pairwise": [comparison.to_dict() for comparison in self.pairwise],
        }


@dataclass(frozen=True, slots=True)
class OverlapRiskAuditSummary:
    """Hash-bound cross-dataset findings used for leakage-risk sensitivity."""

    source: str
    manifest_sha256: str
    is_valid: bool
    error_count: int
    warning_count: int
    confirmed_task_ids: tuple[int, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "manifest_sha256": self.manifest_sha256,
            "manifest_sha256_policy": CANONICAL_TEXT_SHA256_POLICY,
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "confirmed_task_ids": list(self.confirmed_task_ids),
            "historical_model_binding": {
                "recorded": False,
                "value": None,
                "note": (
                    "the repository does not bind this exact training export to the "
                    "evaluated fine-tuned model"
                ),
            },
        }


@dataclass(frozen=True, slots=True)
class BenchmarkAlignmentSummary:
    """Agreement between benchmark IDs and the union of result IDs."""

    benchmark_only_ids: tuple[int, ...]
    result_only_ids: tuple[int, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "is_aligned": not self.benchmark_only_ids and not self.result_only_ids,
            "benchmark_only_ids": list(self.benchmark_only_ids),
            "result_only_ids": list(self.result_only_ids),
        }


@dataclass(frozen=True, slots=True)
class AnalysisReport:
    """Serializable evidence bundle for historical result comparisons."""

    task_union_ids: tuple[int, ...]
    task_union_sha256: str
    arms: tuple[ArmSummary, ...]
    complete_cases: CompleteCaseSummary
    pairwise: tuple[PairwiseComparison, ...]
    issues: tuple[ReportIssue, ...]
    benchmark_audit: BenchmarkAuditSummary | None = None
    benchmark_alignment: BenchmarkAlignmentSummary | None = None
    sensitivity: SensitivitySummary | None = None
    overlap_risk_audit: OverlapRiskAuditSummary | None = None
    overlap_risk_sensitivity: SensitivitySummary | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": "1.3",
            "analysis": "historical paired correctness comparison",
            "analyzer": {
                "package": "prompt-refinement-eval",
                "version": __version__,
                "settings": {
                    "pairing_key": "task_id",
                    "accepted_status": "Accepted",
                    "complete_case_rule": "exact task-ID intersection",
                    "paired_test": "two-sided exact McNemar (binomial)",
                    "multiple_comparison_adjustment": "none",
                    "fingerprint_policies": {
                        CANONICAL_JSON_SHA256_POLICY: (
                            "JSON sorted by key with compact separators, encoded as UTF-8, "
                            "then hashed with SHA-256"
                        ),
                        CANONICAL_TEXT_SHA256_POLICY: (
                            "UTF-8 text with an optional BOM removed and CRLF or CR newlines "
                            "normalized to LF, then hashed with SHA-256"
                        ),
                    },
                },
            },
            "task_union": {
                "task_count": len(self.task_union_ids),
                "task_ids": list(self.task_union_ids),
                "sha256": self.task_union_sha256,
                "sha256_policy": CANONICAL_JSON_SHA256_POLICY,
            },
            "arms": {arm.name: arm.to_dict() for arm in self.arms},
            "complete_cases": self.complete_cases.to_dict(),
            "pairwise": [comparison.to_dict() for comparison in self.pairwise],
            "benchmark_audit": (
                None if self.benchmark_audit is None else self.benchmark_audit.to_dict()
            ),
            "benchmark_alignment": (
                None if self.benchmark_alignment is None else self.benchmark_alignment.to_dict()
            ),
            "sensitivity_analysis": (
                None if self.sensitivity is None else self.sensitivity.to_dict()
            ),
            "overlap_risk_audit": (
                None if self.overlap_risk_audit is None else self.overlap_risk_audit.to_dict()
            ),
            "overlap_risk_sensitivity_analysis": (
                None
                if self.overlap_risk_sensitivity is None
                else self.overlap_risk_sensitivity.to_dict()
            ),
            "issues": [issue.to_dict() for issue in self.issues],
        }


def benchmark_audit_from_validation(
    validation: DatasetValidation,
    *,
    source: Path,
    task_ids: Sequence[int],
    correction_manifest: Path | None = None,
) -> BenchmarkAuditSummary:
    """Convert benchmark validation into report provenance and sensitivity IDs."""

    flagged_ids = sorted({task_id for issue in validation.issues for task_id in issue.record_ids})
    sensitivity_ids = sorted(
        {
            task_id
            for issue in validation.issues
            if issue.severity == "error" or issue.code in _SENSITIVITY_ISSUE_CODES
            for task_id in issue.record_ids
        }
    )
    validation_bytes = json.dumps(
        validation.to_dict(),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    correction_source: str | None = None
    correction_sha256: str | None = None
    if correction_manifest is not None:
        correction_bytes = correction_manifest.read_bytes()
        correction_value: object = json.loads(correction_bytes)
        if not isinstance(correction_value, dict):
            raise ValueError("correction manifest must be a JSON object")
        if correction_value.get("source_content_sha256") != validation.sha256:
            raise ValueError("correction manifest does not match the benchmark fingerprint")
        correction_source = correction_manifest.as_posix()
        correction_sha256 = canonical_text_sha256(correction_bytes)
    return BenchmarkAuditSummary(
        source=source.as_posix(),
        record_count=validation.record_count,
        sha256=validation.sha256,
        is_valid=validation.is_valid,
        error_count=validation.error_count,
        warning_count=validation.warning_count,
        issue_codes=tuple(sorted({issue.code for issue in validation.issues})),
        validation_summary_sha256=hashlib.sha256(validation_bytes).hexdigest(),
        task_ids=tuple(sorted(task_ids)),
        flagged_task_ids=tuple(flagged_ids),
        sensitivity_excluded_task_ids=tuple(sensitivity_ids),
        correction_manifest_source=correction_source,
        correction_manifest_sha256=correction_sha256,
    )


def overlap_risk_audit_from_validation(
    validation: DatasetValidation,
    *,
    source: Path,
) -> OverlapRiskAuditSummary:
    """Convert a verified overlap manifest audit into analysis provenance."""

    confirmed_ids = sorted(
        {
            task_id
            for issue in validation.issues
            if issue.code == "cross_dataset.confirmed_task_overlap"
            for task_id in issue.record_ids
        }
    )
    return OverlapRiskAuditSummary(
        source=source.as_posix(),
        manifest_sha256=validation.sha256,
        is_valid=validation.is_valid,
        error_count=validation.error_count,
        warning_count=validation.warning_count,
        confirmed_task_ids=tuple(confirmed_ids),
    )


def load_historical_result(path: Path, name: str | None = None) -> HistoricalArm:
    """Load and integrity-check one ``*_score_readable.json`` artifact."""

    arm_name = name or path.stem
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        raise ResultFormatError(path, str(exc)) from exc
    try:
        root: object = json.loads(raw_bytes, object_pairs_hook=_unique_json_object)
    except _DuplicateJsonKey as exc:
        raise ResultFormatError(path, f"duplicate JSON object key {exc.key!r}") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ResultFormatError(path, f"invalid JSON: {exc}") from exc
    if not isinstance(root, dict):
        raise ResultFormatError(path, "top-level value must be a JSON object")
    detail = root.get("detail")
    if not isinstance(detail, dict):
        raise ResultFormatError(path, "top-level 'detail' must be a JSON object keyed by task ID")

    issues: list[ReportIssue] = []
    records: dict[int, ResultRecord] = {}
    for raw_task_id, raw_record in detail.items():
        if not isinstance(raw_task_id, str) or _CANONICAL_TASK_ID.fullmatch(raw_task_id) is None:
            raise ResultFormatError(
                path,
                f"detail key {raw_task_id!r} is not a canonical positive integer ID",
            )
        task_id = int(raw_task_id)
        if task_id in records:
            raise ResultFormatError(path, f"duplicate normalized task ID {task_id}")
        if not isinstance(raw_record, dict):
            raise ResultFormatError(path, f"detail[{raw_task_id!r}] must be a JSON object")
        status_value = raw_record.get("status_msg")
        if not isinstance(status_value, str) or not status_value.strip():
            status_code = raw_record.get("status_code")
            status = "Accepted" if status_code == 10 else "Unknown"
            issues.append(
                ReportIssue(
                    code="result.missing_status",
                    arm=arm_name,
                    message=(
                        f"task {task_id} has no non-empty status_msg; interpreted as {status!r} "
                        f"from status_code={status_code!r}"
                    ),
                )
            )
        else:
            status = status_value.strip()
        records[task_id] = ResultRecord(
            task_id=task_id,
            status=status,
            accepted=_is_accepted(status),
            task_finish_time_ms=_task_finish_time(raw_record, task_id, arm_name, issues),
        )

    declared_total = _declared_count(root, "total", arm_name, issues)
    declared_success = _declared_count(root, "success", arm_name, issues)
    declared_failed = _declared_count(root, "failed", arm_name, issues)
    observed_total = len(records)
    observed_success = sum(record.accepted for record in records.values())
    observed_failed = observed_total - observed_success
    _check_declared_count(arm_name, "total", declared_total, observed_total, issues)
    _check_declared_count(arm_name, "success", declared_success, observed_success, issues)
    _check_declared_count(arm_name, "failed", declared_failed, observed_failed, issues)

    return HistoricalArm(
        name=arm_name,
        source=path,
        source_sha256=canonical_text_sha256(raw_bytes),
        records=records,
        declared_total=declared_total,
        declared_success=declared_success,
        declared_failed=declared_failed,
        issues=tuple(issues),
    )


def analyze_historical_results(
    result_paths: Mapping[str, Path],
    *,
    benchmark_audit: BenchmarkAuditSummary | None = None,
    overlap_risk_audit: OverlapRiskAuditSummary | None = None,
) -> AnalysisReport:
    """Load result arms and compare correctness on ID-keyed paired intersections."""

    if len(result_paths) < 2:
        raise ValueError("at least two historical result arms are required")
    arms = tuple(
        load_historical_result(Path(path), name=name) for name, path in sorted(result_paths.items())
    )
    task_union = tuple(sorted(set().union(*(set(arm.records) for arm in arms))))
    task_union_set = set(task_union)
    complete_ids = tuple(sorted(set.intersection(*(set(arm.records) for arm in arms))))
    benchmark_alignment: BenchmarkAlignmentSummary | None = None
    if benchmark_audit is not None:
        if not benchmark_audit.is_valid:
            raise ValueError(
                "benchmark validation failed; resolve its structural errors before analysis"
            )
        benchmark_ids = set(benchmark_audit.task_ids)
        benchmark_alignment = BenchmarkAlignmentSummary(
            benchmark_only_ids=tuple(sorted(benchmark_ids - task_union_set)),
            result_only_ids=tuple(sorted(task_union_set - benchmark_ids)),
        )
        if benchmark_alignment.result_only_ids:
            unexpected = ", ".join(map(str, benchmark_alignment.result_only_ids))
            raise ValueError(f"result task IDs are absent from the benchmark: {unexpected}")
    if overlap_risk_audit is not None:
        if not overlap_risk_audit.is_valid:
            raise ValueError("train/benchmark overlap manifest validation failed")
        unexpected_overlap_ids = set(overlap_risk_audit.confirmed_task_ids) - task_union_set
        if unexpected_overlap_ids:
            unexpected = ", ".join(map(str, sorted(unexpected_overlap_ids)))
            raise ValueError(f"overlap task IDs are absent from the result union: {unexpected}")

    summaries: list[ArmSummary] = []
    complete_arms: list[CompleteCaseArm] = []
    for arm in arms:
        accepted = sum(record.accepted for record in arm.records.values())
        observed_total = len(arm.records)
        failures = Counter(record.status for record in arm.records.values() if not record.accepted)
        finish_times = [
            record.task_finish_time_ms
            for record in arm.records.values()
            if record.task_finish_time_ms is not None
        ]
        summaries.append(
            ArmSummary(
                name=arm.name,
                source=arm.source.as_posix(),
                source_sha256=arm.source_sha256,
                declared_total=arm.declared_total,
                declared_success=arm.declared_success,
                declared_failed=arm.declared_failed,
                observed_total=observed_total,
                accepted=accepted,
                failed=observed_total - accepted,
                acceptance_rate=_rate(accepted, observed_total),
                failure_distribution=dict(sorted(failures.items())),
                missing_ids=tuple(sorted(task_union_set - set(arm.records))),
                observed_run_started_at=(
                    _timestamp_iso(min(finish_times)) if finish_times else None
                ),
                observed_run_ended_at=(_timestamp_iso(max(finish_times)) if finish_times else None),
                archival_run=_archival_run_metadata(arm.name, arm.source_sha256),
            )
        )
        complete_accepted = sum(arm.records[task_id].accepted for task_id in complete_ids)
        complete_arms.append(
            CompleteCaseArm(
                name=arm.name,
                accepted=complete_accepted,
                failed=len(complete_ids) - complete_accepted,
                acceptance_rate=_rate(complete_accepted, len(complete_ids)),
            )
        )

    pairwise = tuple(_compare_pair(arm_a, arm_b) for arm_a, arm_b in combinations(arms, 2))
    sensitivity: SensitivitySummary | None = None
    if benchmark_audit is not None and benchmark_audit.sensitivity_excluded_task_ids:
        sensitivity = _build_sensitivity_summary(
            arms,
            task_union,
            complete_ids,
            excluded_task_ids=benchmark_audit.sensitivity_excluded_task_ids,
            reason="exclude benchmark tasks with identity-level validation findings",
        )
    overlap_risk_sensitivity: SensitivitySummary | None = None
    if overlap_risk_audit is not None and overlap_risk_audit.confirmed_task_ids:
        overlap_risk_sensitivity = _build_sensitivity_summary(
            arms,
            task_union,
            complete_ids,
            excluded_task_ids=overlap_risk_audit.confirmed_task_ids,
            reason=(
                "exclude benchmark tasks with equivalent variants in the retained training export"
            ),
        )
    all_issues = tuple(issue for arm in arms for issue in arm.issues)
    return AnalysisReport(
        task_union_ids=task_union,
        task_union_sha256=_id_fingerprint(task_union),
        arms=tuple(summaries),
        complete_cases=CompleteCaseSummary(
            task_ids=complete_ids,
            arms=tuple(complete_arms),
        ),
        pairwise=pairwise,
        issues=all_issues,
        benchmark_audit=benchmark_audit,
        benchmark_alignment=benchmark_alignment,
        sensitivity=sensitivity,
        overlap_risk_audit=overlap_risk_audit,
        overlap_risk_sensitivity=overlap_risk_sensitivity,
    )


def _build_sensitivity_summary(
    arms: Sequence[HistoricalArm],
    task_union: tuple[int, ...],
    complete_ids: tuple[int, ...],
    *,
    excluded_task_ids: tuple[int, ...],
    reason: str,
) -> SensitivitySummary:
    excluded = frozenset(excluded_task_ids)
    sensitivity_complete_ids = tuple(task_id for task_id in complete_ids if task_id not in excluded)
    sensitivity_complete_arms: list[CompleteCaseArm] = []
    for arm in arms:
        accepted = sum(arm.records[task_id].accepted for task_id in sensitivity_complete_ids)
        sensitivity_complete_arms.append(
            CompleteCaseArm(
                name=arm.name,
                accepted=accepted,
                failed=len(sensitivity_complete_ids) - accepted,
                acceptance_rate=_rate(accepted, len(sensitivity_complete_ids)),
            )
        )
    return SensitivitySummary(
        reason=reason,
        excluded_task_ids=excluded_task_ids,
        retained_union_ids=tuple(task_id for task_id in task_union if task_id not in excluded),
        complete_case_ids=sensitivity_complete_ids,
        complete_case_arms=tuple(sensitivity_complete_arms),
        pairwise=tuple(
            _compare_pair(arm_a, arm_b, excluded_ids=excluded)
            for arm_a, arm_b in combinations(arms, 2)
        ),
    )


def exact_mcnemar_p_value(a_only_accepted: int, b_only_accepted: int) -> float:
    """Return the two-sided exact McNemar p-value for discordant pair counts.

    Under the null, either arm is equally likely to own each discordant success,
    so the smaller tail follows ``Binomial(n, 0.5)``. The doubled tail is capped
    at one, matching the conventional exact McNemar test.
    """

    if a_only_accepted < 0 or b_only_accepted < 0:
        raise ValueError("discordant counts must be non-negative")
    discordant = a_only_accepted + b_only_accepted
    if discordant == 0:
        return 1.0
    lower = min(a_only_accepted, b_only_accepted)
    tail_numerator = sum(math.comb(discordant, value) for value in range(lower + 1))
    p_value = (2 * tail_numerator) / (1 << discordant)
    return min(1.0, p_value)


def write_report_json(report: AnalysisReport | Mapping[str, object], path: Path) -> None:
    """Write an analysis report as deterministic, human-readable JSON."""

    payload: Mapping[str, object] = (
        report.to_dict() if isinstance(report, AnalysisReport) else report
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    path.write_text(f"{serialized}\n", encoding="utf-8", newline="\n")


def _compare_pair(
    arm_a: HistoricalArm,
    arm_b: HistoricalArm,
    *,
    excluded_ids: frozenset[int] = _EMPTY_IDS,
) -> PairwiseComparison:
    ids_a = set(arm_a.records) - excluded_ids
    ids_b = set(arm_b.records) - excluded_ids
    paired_ids = tuple(sorted(ids_a & ids_b))
    if not paired_ids:
        raise ValueError(
            f"arms {arm_a.name!r} and {arm_b.name!r} have no shared task IDs to compare"
        )
    both_accepted = 0
    both_failed = 0
    a_only_accepted = 0
    b_only_accepted = 0
    for task_id in paired_ids:
        is_accepted_a = arm_a.records[task_id].accepted
        is_accepted_b = arm_b.records[task_id].accepted
        if is_accepted_a and is_accepted_b:
            both_accepted += 1
        elif is_accepted_a:
            a_only_accepted += 1
        elif is_accepted_b:
            b_only_accepted += 1
        else:
            both_failed += 1
    accepted_count_a = both_accepted + a_only_accepted
    accepted_count_b = both_accepted + b_only_accepted
    rate_a = _rate(accepted_count_a, len(paired_ids))
    rate_b = _rate(accepted_count_b, len(paired_ids))
    difference = None if rate_a is None or rate_b is None else rate_b - rate_a
    return PairwiseComparison(
        arm_a=arm_a.name,
        arm_b=arm_b.name,
        paired_ids=paired_ids,
        only_a_ids=tuple(sorted(ids_a - ids_b)),
        only_b_ids=tuple(sorted(ids_b - ids_a)),
        both_accepted=both_accepted,
        both_failed=both_failed,
        a_only_accepted=a_only_accepted,
        b_only_accepted=b_only_accepted,
        arm_a_accepted=accepted_count_a,
        arm_b_accepted=accepted_count_b,
        arm_a_acceptance_rate=rate_a,
        arm_b_acceptance_rate=rate_b,
        acceptance_rate_difference_b_minus_a=difference,
        mcnemar_exact_p_value=exact_mcnemar_p_value(a_only_accepted, b_only_accepted),
    )


def _task_finish_time(
    raw_record: Mapping[object, object],
    task_id: int,
    arm_name: str,
    issues: list[ReportIssue],
) -> int | None:
    value = raw_record.get("task_finish_time")
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        issues.append(
            ReportIssue(
                code="result.invalid_task_finish_time",
                arm=arm_name,
                message=f"task {task_id} has invalid task_finish_time={value!r}",
            )
        )
        return None
    return value


def _timestamp_iso(milliseconds: int) -> str:
    timestamp = datetime.fromtimestamp(milliseconds / 1000, tz=timezone.utc)
    return timestamp.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _archival_run_metadata(name: str, source_sha256: str) -> ArchivalRunMetadata:
    strategies: dict[str, tuple[str, str, str | None]] = {
        "baseline_gpt35": ("direct generation", "GPT-3.5", None),
        "finetuned_refiner_gpt35": (
            "fine-tuned prompt refinement then generation",
            "GPT-3.5",
            "fine-tuned GPT-4o",
        ),
        "gpt4o_refiner_gpt35": (
            "general prompt refinement then generation",
            "GPT-3.5",
            "GPT-4o",
        ),
    }
    strategy, generator, refiner = strategies.get(
        name,
        (name, "not recorded", "not recorded"),
    )
    return ArchivalRunMetadata(
        run_id=f"historical-{source_sha256[:12]}",
        strategy=strategy,
        generator_label=generator,
        refiner_label=refiner,
    )


def _declared_count(
    root: Mapping[object, object],
    field: str,
    arm_name: str,
    issues: list[ReportIssue],
) -> int | None:
    value = root.get(field)
    if value is None:
        issues.append(
            ReportIssue(
                code="result.missing_declared_count",
                arm=arm_name,
                message=f"top-level {field!r} is missing",
            )
        )
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        issues.append(
            ReportIssue(
                code="result.invalid_declared_count",
                arm=arm_name,
                message=f"top-level {field!r} must be a non-negative integer; found {value!r}",
            )
        )
        return None
    return value


def _check_declared_count(
    arm_name: str,
    field: str,
    declared: int | None,
    observed: int,
    issues: list[ReportIssue],
) -> None:
    if declared is not None and declared != observed:
        issues.append(
            ReportIssue(
                code="result.declared_count_mismatch",
                arm=arm_name,
                message=f"declared {field}={declared}, observed {field}={observed}",
            )
        )


def _is_accepted(status: str) -> bool:
    return " ".join(status.casefold().split()) == "accepted"


def _rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def _id_fingerprint(ids: Sequence[int]) -> str:
    payload = json.dumps(list(ids), separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJsonKey(key)
        result[key] = value
    return result
