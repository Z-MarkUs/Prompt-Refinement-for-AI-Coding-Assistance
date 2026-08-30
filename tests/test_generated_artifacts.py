from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised by the Python 3.10 CI job
    import tomli as tomllib

from prompt_refinement_eval import __version__
from prompt_refinement_eval.analysis import exact_mcnemar_p_value
from prompt_refinement_eval.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_committed_analysis_and_markdown_are_fresh(tmp_path: Path) -> None:
    regenerated_markdown = tmp_path / "results.md"
    regenerated_json = tmp_path / "historical-analysis.json"

    status = main(
        [
            "report",
            "--output",
            str(regenerated_markdown),
            "--analysis-output",
            str(regenerated_json),
        ]
    )

    assert status == 0
    assert regenerated_json.read_bytes() == (ROOT / "results/historical-analysis.json").read_bytes()
    assert regenerated_markdown.read_bytes() == (ROOT / "docs/results.md").read_bytes()


def test_committed_validation_audit_is_fresh(tmp_path: Path) -> None:
    regenerated = tmp_path / "data-validation.json"

    status = main(["validate", "--output", str(regenerated)])

    assert status == 1
    assert regenerated.read_bytes() == (ROOT / "results/data-validation.json").read_bytes()


def test_readme_and_site_metrics_match_generated_analysis() -> None:
    analysis = json.loads((ROOT / "results/historical-analysis.json").read_text(encoding="utf-8"))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    site = (ROOT / "site/index.html").read_text(encoding="utf-8")
    labels = {
        "baseline_gpt35": "Direct GPT-3.5",
        "finetuned_refiner_gpt35": "Fine-tuned refiner",
        "gpt4o_refiner_gpt35": "GPT-4o refiner",
    }

    for arm_id, label in labels.items():
        arm = analysis["arms"][arm_id]
        accepted = arm["accepted"]
        observed = arm["observed_total"]
        rate = arm["acceptance_rate"]
        assert f"{accepted} / {observed}" in readme
        assert f"{rate * 100:.2f}%" in readme
        assert f"{accepted} / {observed} accepted" in site
        assert f"{rate * 100:.1f}%" in site
        assert label in readme
        assert label in site

    complete_arms = analysis["complete_cases"]["arms"]
    for arm_id in labels:
        arm = complete_arms[arm_id]
        assert f"{arm['accepted']} / 193 ({arm['acceptance_rate'] * 100:.2f}%)" in readme
        assert f">{arm['accepted']}</td><td>193</td>" in site

    comparison = next(
        item
        for item in analysis["pairwise"]
        if item["arm_a"] == "baseline_gpt35" and item["arm_b"] == "finetuned_refiner_gpt35"
    )
    assert comparison["paired_count"] == 194
    assert comparison["contingency"]["a_only_accepted"] == 23
    assert comparison["contingency"]["b_only_accepted"] == 16
    assert "0.3368" in readme
    assert "0.3368" in site

    sensitivity = next(
        item
        for item in analysis["sensitivity_analysis"]["pairwise"]
        if item["arm_a"] == "baseline_gpt35" and item["arm_b"] == "finetuned_refiner_gpt35"
    )
    assert sensitivity["paired_count"] == 191
    assert sensitivity["contingency"]["a_only_accepted"] == 22
    assert sensitivity["contingency"]["b_only_accepted"] == 16
    assert "0.4177" in readme
    assert "0.4177" in site


def test_readme_local_links_resolve() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    targets = re.findall(r"\[[^]]+\]\(([^)]+)\)", readme)

    local_targets = [target.split("#", 1)[0] for target in targets if "://" not in target]
    assert local_targets
    for target in local_targets:
        assert (ROOT / target).exists(), f"README link does not resolve: {target}"


def test_readme_model_example_tracks_the_public_pipeline_api() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    for current_api in (
        "PROMPT_EVAL_RUN_ID",
        "RunContext(",
        "run_id=config.run_id",
        'arm_id="direct"',
        'strategy_version="direct-v1"',
        "generator=config.generator_stage()",
    ):
        assert current_api in readme
    assert "ExperimentArm(name=" not in readme
    assert "PROMPT_EVAL_TEMPERATURE" not in readme


def test_release_metadata_versions_stay_in_sync() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    citation_version = re.search(r"^version: (.+)$", citation, flags=re.MULTILINE)

    assert citation_version is not None
    assert pyproject["project"]["version"] == __version__
    assert citation_version.group(1) == __version__
    assert (
        "/THIRD_PARTY_NOTICES.md"
        in pyproject["tool"]["hatch"]["build"]["targets"]["sdist"]["include"]
    )
    assert (
        "/constraints/ci.txt" in pyproject["tool"]["hatch"]["build"]["targets"]["sdist"]["include"]
    )


def test_workflows_pin_actions_and_pages_only_deploys_a_green_main_push() -> None:
    workflows = [
        (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"),
        (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8"),
    ]
    for workflow in workflows:
        actions = re.findall(r"uses:\s+[^@\s]+@([^\s#]+)", workflow)
        assert actions
        assert all(re.fullmatch(r"[0-9a-f]{40}", revision) for revision in actions)

    pages = workflows[1]
    assert "--constraint constraints/ci.txt" in workflows[0]
    assert "workflow_run:" in pages
    assert "conclusion == 'success'" in pages
    assert "workflow_run.event == 'push'" in pages
    assert "head_branch == 'main'" in pages
    assert "workflow_dispatch:" not in pages


def test_raw_judge_records_exactly_reconcile_to_summaries_and_id_mapping() -> None:
    mapping_payload = json.loads(
        (ROOT / "AutoTest/leetcode_question_id_slug_mapping.json").read_text(encoding="utf-8")
    )
    mapping_items = mapping_payload["question_id_mapping"]
    frontend_to_internal = {
        str(item["frontend_question_id"]): str(item["question_id"]) for item in mapping_items
    }
    assert len(frontend_to_internal) == len(mapping_items)
    summary_names = {
        "3.5": "3.5_score_readable.json",
        "finetuned": "finetuned_score_readable.json",
        "4o_3.5": "4o_3.5_score_readable.json",
    }
    submission_ids: set[str] = set()

    for directory_name, summary_name in summary_names.items():
        raw_directory = ROOT / "AutoTest" / "leetcode_verify" / directory_name
        raw_records = {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in raw_directory.glob("*.json")
        }
        summary = json.loads(
            (ROOT / "AutoTest" / "leetcode_summary" / summary_name).read_text(encoding="utf-8")
        )
        detail = summary["detail"]

        assert set(raw_records) == set(detail)
        accepted = 0
        for frontend_id, raw_record in raw_records.items():
            assert raw_record == detail[frontend_id]
            assert str(raw_record["question_id"]) == frontend_to_internal[frontend_id]
            submission_id = str(raw_record["submission_id"])
            assert submission_id not in submission_ids
            submission_ids.add(submission_id)
            accepted += raw_record["status_msg"] == "Accepted"

        assert summary["total"] == len(raw_records)
        assert summary["success"] == accepted
        assert summary["failed"] == len(raw_records) - accepted

    assert len(submission_ids) == 592


def test_disclosed_overlap_exclusion_leaves_paired_conclusion_unchanged() -> None:
    direct = json.loads(
        (ROOT / "AutoTest/leetcode_summary/3.5_score_readable.json").read_text(encoding="utf-8")
    )["detail"]
    refined = json.loads(
        (ROOT / "AutoTest/leetcode_summary/finetuned_score_readable.json").read_text(
            encoding="utf-8"
        )
    )["detail"]
    excluded = {"1009", "1038"}
    paired_ids = (set(direct) & set(refined)) - excluded
    direct_only = sum(
        direct[task_id]["status_msg"] == "Accepted" and refined[task_id]["status_msg"] != "Accepted"
        for task_id in paired_ids
    )
    refined_only = sum(
        direct[task_id]["status_msg"] != "Accepted" and refined[task_id]["status_msg"] == "Accepted"
        for task_id in paired_ids
    )

    assert len(paired_ids) == 192
    assert (direct_only, refined_only) == (23, 16)
    assert exact_mcnemar_p_value(direct_only, refined_only) == pytest.approx(0.3367836)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    site = (ROOT / "site/index.html").read_text(encoding="utf-8")
    assert "leaves 192 pairs" in readme
    assert "leaves 192 pairs" in site
