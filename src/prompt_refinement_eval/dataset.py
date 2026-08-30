"""Typed loaders and validation for the repository's benchmark datasets.

The legacy benchmark is intentionally treated as immutable evidence.  This module
reports defects with task IDs and source lines so callers can create a curated
revision without silently changing the historical input.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

IssueSeverity = Literal["error", "warning"]

_ALLOWED_DIFFICULTIES = frozenset({"Easy", "Medium", "Hard"})
_IDENTIFIER_PART = re.compile(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+")
_WORD = re.compile(r"[A-Za-z][A-Za-z0-9_]*")
_SIGNATURE_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "arr",
        "array",
        "def",
        "find",
        "get",
        "has",
        "in",
        "int",
        "is",
        "list",
        "max",
        "min",
        "of",
        "self",
        "solution",
        "str",
        "the",
        "to",
    }
)


class DatasetFormatError(ValueError):
    """Raised when a source record cannot be represented by the typed model."""

    def __init__(self, path: Path, line_number: int, message: str) -> None:
        self.path = path
        self.line_number = line_number
        self.problem = message
        super().__init__(f"{path}:{line_number}: {message}")


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    """One task from ``AutoTest/test.csv``."""

    task_id: int
    difficulty: str
    description: str
    signature: str
    source_line: int

    @property
    def id(self) -> int:
        """Compatibility alias for consumers that call the task key ``id``."""

        return self.task_id

    @property
    def method_name(self) -> str | None:
        """Return the single ``Solution`` entry-point method, when detectable."""

        if _class_names(self.signature) != ("Solution",):
            return None
        methods = tuple(name for name in _method_names(self.signature) if not name.startswith("__"))
        return methods[0] if len(methods) == 1 else None


@dataclass(frozen=True, slots=True)
class FineTuningMessage:
    """One chat message in a fine-tuning conversation."""

    role: str
    content: str


@dataclass(frozen=True, slots=True)
class FineTuningExample:
    """One JSONL training or validation example."""

    messages: tuple[FineTuningMessage, ...]
    source_line: int


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """A machine-readable dataset quality finding."""

    code: str
    severity: IssueSeverity
    message: str
    record_ids: tuple[int, ...] = ()
    line_numbers: tuple[int, ...] = ()
    field: str | None = None

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""

        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "record_ids": list(self.record_ids),
            "line_numbers": list(self.line_numbers),
            "field": self.field,
        }


@dataclass(frozen=True, slots=True)
class DatasetValidation:
    """Validation outcome plus an immutable fingerprint of evaluated records."""

    dataset: str
    record_count: int
    sha256: str
    issues: tuple[ValidationIssue, ...]

    @property
    def error_count(self) -> int:
        return sum(issue.severity == "error" for issue in self.issues)

    @property
    def warning_count(self) -> int:
        return sum(issue.severity == "warning" for issue in self.issues)

    @property
    def is_valid(self) -> bool:
        return self.error_count == 0

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""

        return {
            "dataset": self.dataset,
            "record_count": self.record_count,
            "sha256": self.sha256,
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def load_benchmark(path: Path) -> list[BenchmarkCase]:
    """Load a headerless (or explicitly headed) four-column benchmark CSV.

    CSV quoting and multiline fields are handled by :mod:`csv`. Records whose
    physical structure or ID cannot be represented raise :class:`DatasetFormatError`;
    semantic quality checks are returned by :func:`validate_benchmark`.
    """

    cases: list[BenchmarkCase] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        previous_end_line = 0
        for logical_row, row in enumerate(reader, start=1):
            source_line = previous_end_line + 1
            previous_end_line = reader.line_num
            if logical_row == 1 and _is_benchmark_header(row):
                continue
            if len(row) != 4:
                raise DatasetFormatError(
                    path,
                    source_line,
                    f"expected 4 CSV columns, found {len(row)}",
                )
            raw_id, difficulty, description, signature = row
            try:
                task_id = int(raw_id.strip())
            except ValueError as exc:
                raise DatasetFormatError(
                    path,
                    source_line,
                    f"task ID must be an integer, found {raw_id!r}",
                ) from exc
            cases.append(
                BenchmarkCase(
                    task_id=task_id,
                    difficulty=difficulty.strip(),
                    description=description.strip(),
                    signature=signature.rstrip(),
                    source_line=source_line,
                )
            )
    return cases


def validate_benchmark(cases: Sequence[BenchmarkCase]) -> DatasetValidation:
    """Validate task identity, required fields, signatures, and likely mismatches."""

    issues: list[ValidationIssue] = []
    by_id: dict[int, list[BenchmarkCase]] = defaultdict(list)
    by_signature: dict[str, list[BenchmarkCase]] = defaultdict(list)

    for case in cases:
        by_id[case.task_id].append(case)
        if case.task_id <= 0:
            issues.append(
                _case_issue(
                    case,
                    "benchmark.invalid_task_id",
                    "error",
                    "task ID must be positive",
                    "id",
                )
            )
        if case.difficulty not in _ALLOWED_DIFFICULTIES:
            allowed = ", ".join(sorted(_ALLOWED_DIFFICULTIES))
            issues.append(
                _case_issue(
                    case,
                    "benchmark.invalid_difficulty",
                    "error",
                    f"difficulty must be one of {allowed}; found {case.difficulty!r}",
                    "difficulty",
                )
            )
        if not case.description:
            issues.append(
                _case_issue(
                    case,
                    "benchmark.empty_description",
                    "error",
                    "description must not be empty",
                    "description",
                )
            )
        if not case.signature:
            issues.append(
                _case_issue(
                    case,
                    "benchmark.empty_signature",
                    "error",
                    "signature must not be empty",
                    "signature",
                )
            )
            continue

        signature_key = _normalized_signature(case.signature)
        by_signature[signature_key].append(case)
        syntax_error = _signature_syntax_error(case.signature)
        if syntax_error is not None:
            issues.append(
                _case_issue(
                    case,
                    "benchmark.invalid_python_signature",
                    "error",
                    f"signature is not parseable Python: {syntax_error}",
                    "signature",
                )
            )
            continue
        class_names = _class_names(case.signature)
        if len(class_names) != 1:
            issues.append(
                _case_issue(
                    case,
                    "benchmark.entrypoint_class_count",
                    "error",
                    f"expected exactly one top-level interface class, found {len(class_names)}",
                    "signature",
                )
            )
        methods = _method_names(case.signature)
        public_methods = tuple(name for name in methods if not name.startswith("__"))
        if not public_methods:
            issues.append(
                _case_issue(
                    case,
                    "benchmark.missing_entrypoint",
                    "error",
                    "interface must define at least one public method entry point",
                    "signature",
                )
            )
        elif class_names == ("Solution",) and len(public_methods) != 1:
            issues.append(
                _case_issue(
                    case,
                    "benchmark.entrypoint_method_count",
                    "error",
                    "Solution interface must define exactly one public entry-point method",
                    "signature",
                )
            )
        elif class_names and class_names != ("Solution",) and "__init__" not in methods:
            issues.append(
                _case_issue(
                    case,
                    "benchmark.design_interface_constructor",
                    "error",
                    "non-Solution design interface must define an __init__ constructor",
                    "signature",
                )
            )

    for task_id, duplicates in sorted(by_id.items()):
        if len(duplicates) > 1:
            issues.append(
                ValidationIssue(
                    code="benchmark.duplicate_task_id",
                    severity="error",
                    message=f"task ID {task_id} occurs {len(duplicates)} times",
                    record_ids=(task_id,),
                    line_numbers=tuple(case.source_line for case in duplicates),
                    field="id",
                )
            )

    for duplicates in sorted(by_signature.values(), key=lambda group: group[0].task_id):
        if len(duplicates) < 2:
            continue
        ids = tuple(sorted(case.task_id for case in duplicates))
        lines = tuple(
            case.source_line for case in sorted(duplicates, key=lambda item: item.task_id)
        )
        issues.append(
            ValidationIssue(
                code="benchmark.duplicate_signature",
                severity="warning",
                message=(
                    "identical entry-point signature is reused by task IDs "
                    f"{', '.join(map(str, ids))}; confirm that each description "
                    "matches the entry point"
                ),
                record_ids=ids,
                line_numbers=lines,
                field="signature",
            )
        )
        issues.extend(_description_mismatch_candidates(duplicates))

    return DatasetValidation(
        dataset="benchmark",
        record_count=len(cases),
        sha256=benchmark_fingerprint(cases),
        issues=tuple(_sorted_issues(issues)),
    )


def load_jsonl(path: Path) -> list[FineTuningExample]:
    """Load chat-format fine-tuning JSONL into typed examples."""

    examples: list[FineTuningExample] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if not raw_line.strip():
                raise DatasetFormatError(path, line_number, "blank JSONL records are not allowed")
            try:
                value = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                raise DatasetFormatError(
                    path,
                    line_number,
                    f"invalid JSON: {exc.msg} at column {exc.colno}",
                ) from exc
            if not isinstance(value, dict):
                raise DatasetFormatError(path, line_number, "record must be a JSON object")
            raw_messages = value.get("messages")
            if not isinstance(raw_messages, list):
                raise DatasetFormatError(path, line_number, "'messages' must be a JSON array")
            messages: list[FineTuningMessage] = []
            for message_index, raw_message in enumerate(raw_messages, start=1):
                if not isinstance(raw_message, dict):
                    raise DatasetFormatError(
                        path,
                        line_number,
                        f"message {message_index} must be a JSON object",
                    )
                role = raw_message.get("role")
                content = raw_message.get("content")
                if not isinstance(role, str) or not isinstance(content, str):
                    raise DatasetFormatError(
                        path,
                        line_number,
                        f"message {message_index} requires string 'role' and 'content' fields",
                    )
                messages.append(FineTuningMessage(role=role, content=content))
            examples.append(FineTuningExample(messages=tuple(messages), source_line=line_number))
    return examples


def validate_fine_tuning(examples: Sequence[FineTuningExample]) -> DatasetValidation:
    """Validate the repository's system/user/assistant fine-tuning convention."""

    issues: list[ValidationIssue] = []
    user_lines: dict[str, list[int]] = defaultdict(list)
    conversation_lines: dict[tuple[tuple[str, str], ...], list[int]] = defaultdict(list)
    system_prompts: Counter[str] = Counter()

    for example in examples:
        roles = tuple(message.role for message in example.messages)
        if roles != ("system", "user", "assistant"):
            issues.append(
                ValidationIssue(
                    code="fine_tuning.unexpected_role_sequence",
                    severity="error",
                    message=(f"expected roles ('system', 'user', 'assistant'); found {roles!r}"),
                    line_numbers=(example.source_line,),
                    field="messages.role",
                )
            )
        for index, message in enumerate(example.messages):
            if not message.role.strip():
                issues.append(
                    ValidationIssue(
                        code="fine_tuning.empty_role",
                        severity="error",
                        message=f"message {index + 1} has an empty role",
                        line_numbers=(example.source_line,),
                        field=f"messages[{index}].role",
                    )
                )
            if not message.content.strip():
                issues.append(
                    ValidationIssue(
                        code="fine_tuning.empty_content",
                        severity="error",
                        message=f"message {index + 1} has empty content",
                        line_numbers=(example.source_line,),
                        field=f"messages[{index}].content",
                    )
                )

        messages_by_role = {message.role: message for message in example.messages}
        system = messages_by_role.get("system")
        user = messages_by_role.get("user")
        assistant = messages_by_role.get("assistant")
        if system is not None:
            system_prompts[system.content.strip()] += 1
        if user is not None:
            user_lines[_normalized_text(user.content)].append(example.source_line)
        if assistant is not None and assistant.content.strip():
            try:
                assistant_value = json.loads(assistant.content)
            except json.JSONDecodeError as exc:
                issues.append(
                    ValidationIssue(
                        code="fine_tuning.assistant_content_not_json",
                        severity="error",
                        message=f"assistant content is not valid JSON: {exc.msg}",
                        line_numbers=(example.source_line,),
                        field="messages.assistant.content",
                    )
                )
            else:
                if not isinstance(assistant_value, dict):
                    issues.append(
                        ValidationIssue(
                            code="fine_tuning.assistant_content_not_object",
                            severity="error",
                            message="assistant content must encode a JSON object",
                            line_numbers=(example.source_line,),
                            field="messages.assistant.content",
                        )
                    )
                elif not assistant_value:
                    issues.append(
                        ValidationIssue(
                            code="fine_tuning.empty_assistant_object",
                            severity="error",
                            message="assistant content must encode a non-empty JSON object",
                            line_numbers=(example.source_line,),
                            field="messages.assistant.content",
                        )
                    )

        conversation_key = tuple((message.role, message.content) for message in example.messages)
        conversation_lines[conversation_key].append(example.source_line)

    for lines in sorted(user_lines.values(), key=lambda values: values[0]):
        if len(lines) > 1:
            issues.append(
                ValidationIssue(
                    code="fine_tuning.duplicate_user_prompt",
                    severity="warning",
                    message=f"normalized user prompt is repeated on {len(lines)} lines",
                    line_numbers=tuple(lines),
                    field="messages.user.content",
                )
            )
    for lines in sorted(conversation_lines.values(), key=lambda values: values[0]):
        if len(lines) > 1:
            issues.append(
                ValidationIssue(
                    code="fine_tuning.duplicate_conversation",
                    severity="error",
                    message=f"identical conversation is repeated on {len(lines)} lines",
                    line_numbers=tuple(lines),
                    field="messages",
                )
            )
    if len(system_prompts) > 1:
        issues.append(
            ValidationIssue(
                code="fine_tuning.inconsistent_system_prompt",
                severity="warning",
                message=f"dataset contains {len(system_prompts)} distinct system prompts",
                field="messages.system.content",
            )
        )

    return DatasetValidation(
        dataset="fine_tuning",
        record_count=len(examples),
        sha256=fine_tuning_fingerprint(examples),
        issues=tuple(_sorted_issues(issues)),
    )


def validate_train_benchmark_overlaps(
    cases: Sequence[BenchmarkCase],
    examples: Sequence[FineTuningExample],
    manifest_path: Path,
) -> DatasetValidation:
    """Audit exact and curated semantic overlap between training and benchmark tasks.

    Exact matches under the documented normalization policy are hard errors. Semantic
    variants require human review, so the curated manifest binds each decision to source
    fingerprints and normalized component hashes before it can emit a warning.
    """

    issues = _exact_overlap_issues(cases, examples)
    try:
        manifest_bytes = manifest_path.read_bytes()
    except OSError:
        raise
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    try:
        raw_manifest: object = json.loads(manifest_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        issues.append(_overlap_manifest_issue(f"manifest is not valid UTF-8 JSON: {exc}"))
        return DatasetValidation(
            dataset="train_benchmark_overlap",
            record_count=0,
            sha256=manifest_sha256,
            issues=tuple(_sorted_issues(issues)),
        )
    if not isinstance(raw_manifest, dict):
        issues.append(_overlap_manifest_issue("manifest root must be a JSON object"))
        return DatasetValidation(
            dataset="train_benchmark_overlap",
            record_count=0,
            sha256=manifest_sha256,
            issues=tuple(_sorted_issues(issues)),
        )

    manifest: Mapping[object, object] = raw_manifest
    if manifest.get("schema_version") != "1.0":
        issues.append(_overlap_manifest_issue("schema_version must be '1.0'"))
    if manifest.get("normalization") != "nfkc-casefold-ascii-alnum-v1":
        issues.append(
            _overlap_manifest_issue("normalization must be 'nfkc-casefold-ascii-alnum-v1'")
        )

    sources_value = manifest.get("sources")
    if not isinstance(sources_value, dict):
        issues.append(_overlap_manifest_issue("sources must be a JSON object"))
    else:
        issues.extend(
            _overlap_source_issues(
                sources_value,
                benchmark_count=len(cases),
                benchmark_sha256=benchmark_fingerprint(cases),
                train_count=len(examples),
                train_sha256=fine_tuning_fingerprint(examples),
            )
        )

    confirmed_value = manifest.get("confirmed_overlaps")
    reviewed_value = manifest.get("reviewed_non_overlaps")
    confirmed = list(confirmed_value) if isinstance(confirmed_value, list) else []
    reviewed = list(reviewed_value) if isinstance(reviewed_value, list) else []
    if not isinstance(confirmed_value, list):
        issues.append(_overlap_manifest_issue("confirmed_overlaps must be a JSON array"))
    if not isinstance(reviewed_value, list):
        issues.append(_overlap_manifest_issue("reviewed_non_overlaps must be a JSON array"))

    cases_by_id = {case.task_id: case for case in cases}
    examples_by_line = {example.source_line: example for example in examples}
    seen_pairs: set[tuple[int, int]] = set()
    for collection, expected_classification, emit_warning in (
        (confirmed, "equivalent_task_variant", True),
        (reviewed, "related_but_distinct", False),
    ):
        for entry_value in collection:
            if not isinstance(entry_value, dict):
                issues.append(_overlap_manifest_issue("every overlap entry must be an object"))
                continue
            entry: Mapping[object, object] = entry_value
            train_line = _manifest_int(entry, "train_source_line")
            task_id = _manifest_int(entry, "benchmark_task_id")
            benchmark_line = _manifest_int(entry, "benchmark_source_line")
            if train_line is None or task_id is None or benchmark_line is None:
                issues.append(
                    _overlap_manifest_issue(
                        "overlap entries require integer train_source_line, "
                        "benchmark_task_id, and benchmark_source_line"
                    )
                )
                continue
            pair = (train_line, task_id)
            if pair in seen_pairs:
                issues.append(
                    _overlap_manifest_issue(
                        "duplicate overlap decision for train line "
                        f"{train_line} and task {task_id}",
                        record_ids=(task_id,),
                        line_numbers=(train_line, benchmark_line),
                    )
                )
                continue
            seen_pairs.add(pair)
            example = examples_by_line.get(train_line)
            case = cases_by_id.get(task_id)
            entry_errors: list[ValidationIssue] = []
            if entry.get("split") != "train":
                entry_errors.append(_overlap_manifest_issue("overlap split must be 'train'"))
            if entry.get("classification") != expected_classification:
                entry_errors.append(
                    _overlap_manifest_issue(
                        f"classification must be {expected_classification!r}",
                        record_ids=(task_id,),
                    )
                )
            if example is None:
                entry_errors.append(
                    _overlap_manifest_issue(
                        f"train source line {train_line} is absent from the loaded export",
                        record_ids=(task_id,),
                        line_numbers=(train_line,),
                    )
                )
            if case is None:
                entry_errors.append(
                    _overlap_manifest_issue(
                        f"benchmark task {task_id} is absent from the loaded benchmark",
                        record_ids=(task_id,),
                    )
                )
            elif case.source_line != benchmark_line:
                entry_errors.append(
                    _overlap_manifest_issue(
                        f"task {task_id} starts on benchmark line {case.source_line}, not "
                        f"manifest line {benchmark_line}",
                        record_ids=(task_id,),
                        line_numbers=(benchmark_line, case.source_line),
                    )
                )
            if example is not None and case is not None:
                entry_errors.extend(_overlap_entry_hash_issues(entry, example, case))
            issues.extend(entry_errors)
            if emit_warning and not entry_errors:
                issues.append(
                    ValidationIssue(
                        code="cross_dataset.confirmed_task_overlap",
                        severity="warning",
                        message=(
                            "curated review identifies an equivalent task variant in the "
                            "training export; the repository does not record whether this exact "
                            "export was bound to the evaluated fine-tuned model"
                        ),
                        record_ids=(task_id,),
                        line_numbers=(train_line, benchmark_line),
                        field="train.user+assistant.description+benchmark.description",
                    )
                )

    return DatasetValidation(
        dataset="train_benchmark_overlap",
        record_count=len(confirmed),
        sha256=manifest_sha256,
        issues=tuple(_sorted_issues(issues)),
    )


def benchmark_fingerprint(cases: Sequence[BenchmarkCase]) -> str:
    """Return a stable SHA-256 fingerprint of benchmark content and order."""

    records = [
        {
            "id": case.task_id,
            "difficulty": case.difficulty,
            "description": case.description,
            "signature": case.signature,
        }
        for case in cases
    ]
    return _json_sha256(records)


def fine_tuning_fingerprint(examples: Sequence[FineTuningExample]) -> str:
    """Return a stable SHA-256 fingerprint of conversation content and order."""

    records = [
        {
            "messages": [
                {"role": message.role, "content": message.content} for message in example.messages
            ]
        }
        for example in examples
    ]
    return _json_sha256(records)


def _exact_overlap_issues(
    cases: Sequence[BenchmarkCase],
    examples: Sequence[FineTuningExample],
) -> list[ValidationIssue]:
    cases_by_description: dict[str, list[BenchmarkCase]] = defaultdict(list)
    for case in cases:
        normalized = _normalized_overlap_text(case.description)
        if normalized:
            cases_by_description[normalized].append(case)

    issues: list[ValidationIssue] = []
    seen: set[tuple[int, int, str]] = set()
    for example in examples:
        messages = {message.role: message.content for message in example.messages}
        candidates: list[tuple[str, str]] = []
        user = messages.get("user")
        if user:
            candidates.append(("train.user", user))
        assistant = messages.get("assistant")
        if assistant:
            try:
                assistant_value: object = json.loads(assistant)
            except json.JSONDecodeError:
                assistant_value = None
            if isinstance(assistant_value, dict):
                description = assistant_value.get("description")
                if isinstance(description, str):
                    candidates.append(("train.assistant.description", description))
        for field, candidate in candidates:
            normalized = _normalized_overlap_text(candidate)
            for case in cases_by_description.get(normalized, ()):
                key = (example.source_line, case.task_id, field)
                if key in seen:
                    continue
                seen.add(key)
                issues.append(
                    ValidationIssue(
                        code="cross_dataset.exact_text_overlap",
                        severity="error",
                        message=(
                            "normalized training text exactly matches a benchmark description; "
                            "exclude or explicitly redesign the evaluation split"
                        ),
                        record_ids=(case.task_id,),
                        line_numbers=(example.source_line, case.source_line),
                        field=field,
                    )
                )
    return issues


def _overlap_source_issues(
    sources: Mapping[object, object],
    *,
    benchmark_count: int,
    benchmark_sha256: str,
    train_count: int,
    train_sha256: str,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    expected = {
        "benchmark": (benchmark_count, benchmark_sha256),
        "train": (train_count, train_sha256),
    }
    for label, (expected_count, expected_sha256) in expected.items():
        source_value = sources.get(label)
        if not isinstance(source_value, dict):
            issues.append(_overlap_manifest_issue(f"sources.{label} must be an object"))
            continue
        if source_value.get("record_count") != expected_count:
            issues.append(
                _overlap_manifest_issue(
                    f"sources.{label}.record_count does not match the loaded source"
                )
            )
        if source_value.get("content_sha256") != expected_sha256:
            issues.append(
                _overlap_manifest_issue(
                    f"sources.{label}.content_sha256 does not match the loaded source"
                )
            )
    return issues


def _overlap_entry_hash_issues(
    entry: Mapping[object, object],
    example: FineTuningExample,
    case: BenchmarkCase,
) -> list[ValidationIssue]:
    train_line = example.source_line
    task_id = case.task_id
    lines = (train_line, case.source_line)
    messages = {message.role: message.content for message in example.messages}
    user = messages.get("user")
    assistant = messages.get("assistant")
    if user is None or assistant is None:
        return [
            _overlap_manifest_issue(
                "manifest entry points to a conversation without user and assistant messages",
                record_ids=(task_id,),
                line_numbers=lines,
            )
        ]
    try:
        assistant_value: object = json.loads(assistant)
    except json.JSONDecodeError:
        assistant_value = None
    if not isinstance(assistant_value, dict) or not isinstance(
        assistant_value.get("description"), str
    ):
        return [
            _overlap_manifest_issue(
                "manifest entry points to assistant content without a string description",
                record_ids=(task_id,),
                line_numbers=lines,
            )
        ]

    description = assistant_value["description"]
    if not isinstance(description, str):  # pragma: no cover - narrowed above for mypy
        raise TypeError("assistant description must be a string")
    components = {
        "assistant_description": _normalized_overlap_text(description),
        "benchmark_description": _normalized_overlap_text(case.description),
        "user_prompt": _normalized_overlap_text(user),
    }
    hashes_value = entry.get("normalized_component_sha256")
    issues: list[ValidationIssue] = []
    if not isinstance(hashes_value, dict):
        issues.append(
            _overlap_manifest_issue(
                "normalized_component_sha256 must be an object",
                record_ids=(task_id,),
                line_numbers=lines,
            )
        )
    else:
        for component, value in components.items():
            expected_hash = _text_sha256(value)
            if hashes_value.get(component) != expected_hash:
                issues.append(
                    _overlap_manifest_issue(
                        f"{component} hash does not match the loaded source",
                        record_ids=(task_id,),
                        line_numbers=lines,
                    )
                )
    if entry.get("normalized_bundle_sha256") != _json_sha256(components):
        issues.append(
            _overlap_manifest_issue(
                "normalized bundle hash does not match the loaded source",
                record_ids=(task_id,),
                line_numbers=lines,
            )
        )
    return issues


def _normalized_overlap_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return " ".join(re.findall(r"[a-z0-9]+", normalized))


def _text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _manifest_int(entry: Mapping[object, object], key: str) -> int | None:
    value = entry.get(key)
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _overlap_manifest_issue(
    message: str,
    *,
    record_ids: tuple[int, ...] = (),
    line_numbers: tuple[int, ...] = (),
) -> ValidationIssue:
    return ValidationIssue(
        code="cross_dataset.manifest_mismatch",
        severity="error",
        message=message,
        record_ids=record_ids,
        line_numbers=line_numbers,
        field="overlap_manifest",
    )


def _is_benchmark_header(row: list[str]) -> bool:
    if len(row) != 4:
        return False
    normalized = tuple(value.strip().lower().replace("_", " ") for value in row)
    return normalized in {
        ("id", "difficulty", "description", "signature"),
        ("task id", "difficulty", "description", "signature"),
    }


def _case_issue(
    case: BenchmarkCase,
    code: str,
    severity: IssueSeverity,
    message: str,
    field: str,
) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        severity=severity,
        message=message,
        record_ids=(case.task_id,),
        line_numbers=(case.source_line,),
        field=field,
    )


def _normalized_signature(signature: str) -> str:
    return " ".join(signature.split())


def _signature_syntax_error(signature: str) -> str | None:
    candidate = _completed_signature(signature)
    if not candidate:
        return "empty input"
    try:
        ast.parse(candidate)
    except SyntaxError as exc:
        return exc.msg
    return None


def _class_names(signature: str) -> tuple[str, ...]:
    try:
        tree = ast.parse(_completed_signature(signature))
    except SyntaxError:
        return ()
    return tuple(node.name for node in tree.body if isinstance(node, ast.ClassDef))


def _method_names(signature: str) -> tuple[str, ...]:
    try:
        tree = ast.parse(_completed_signature(signature))
    except SyntaxError:
        return ()
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    if len(classes) != 1:
        return ()
    return tuple(
        child.name
        for child in classes[0].body
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
    )


def _completed_signature(signature: str) -> str:
    lines = signature.rstrip().splitlines()
    completed: list[str] = []
    for index, line in enumerate(lines):
        completed.append(line)
        stripped = line.strip()
        if not stripped.endswith(":") or not stripped.startswith(("class ", "def ", "async def ")):
            continue

        indentation = len(line) - len(line.lstrip())
        has_body = False
        for following in lines[index + 1 :]:
            following_stripped = following.strip()
            if not following_stripped or following_stripped.startswith("#"):
                continue
            following_indent = len(following) - len(following.lstrip())
            has_body = following_indent > indentation
            break
        if not has_body:
            completed.append(f"{' ' * (indentation + 4)}pass")
    return "\n".join(completed)


def _description_mismatch_candidates(
    cases: Sequence[BenchmarkCase],
) -> list[ValidationIssue]:
    scored = [(case, _signature_description_overlap(case)) for case in cases]
    positive_scores = [score for _, score in scored if score > 0]
    if not positive_scores:
        return []
    strongest = max(positive_scores)
    if sum(score == strongest for _, score in scored) != 1:
        return []
    issues: list[ValidationIssue] = []
    for case, score in scored:
        if score != 0:
            continue
        method = case.method_name or "entry point"
        issues.append(
            _case_issue(
                case,
                "benchmark.signature_description_mismatch",
                "warning",
                (
                    f"{method!r} shares no meaningful identifier terms with this description, "
                    "while another task reusing the signature does; review task identity"
                ),
                "signature",
            )
        )
    return issues


def _signature_description_overlap(case: BenchmarkCase) -> int:
    signature_terms: set[str] = set()
    for identifier in _WORD.findall(case.signature):
        for part in _IDENTIFIER_PART.findall(identifier):
            term = part.lower()
            if len(term) > 1 and term not in _SIGNATURE_STOPWORDS:
                signature_terms.add(_singular(term))
    description_terms = {
        _singular(word.lower())
        for word in _WORD.findall(case.description)
        if len(word) > 1 and word.lower() not in _SIGNATURE_STOPWORDS
    }
    return len(signature_terms & description_terms)


def _singular(term: str) -> str:
    if term.endswith("ies") and len(term) > 4:
        return f"{term[:-3]}y"
    if term.endswith("s") and not term.endswith("ss") and len(term) > 3:
        return term[:-1]
    return term


def _normalized_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _json_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _sorted_issues(issues: Sequence[ValidationIssue]) -> list[ValidationIssue]:
    return sorted(
        issues,
        key=lambda issue: (
            0 if issue.severity == "error" else 1,
            issue.line_numbers[0] if issue.line_numbers else 0,
            issue.code,
        ),
    )
