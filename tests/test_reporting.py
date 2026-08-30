from __future__ import annotations

import json
from pathlib import Path

from prompt_refinement_eval.analysis import analyze_historical_results
from prompt_refinement_eval.reporting import render_markdown


def _write_arm(path: Path, statuses: dict[int, str]) -> None:
    accepted = sum(status == "Accepted" for status in statuses.values())
    path.write_text(
        json.dumps(
            {
                "total": len(statuses),
                "success": accepted,
                "failed": len(statuses) - accepted,
                "detail": {
                    str(task_id): {"status_msg": status} for task_id, status in statuses.items()
                },
            }
        ),
        encoding="utf-8",
    )


def test_markdown_report_keeps_negative_result_and_provenance_visible(tmp_path: Path) -> None:
    baseline = tmp_path / "baseline.json"
    refined = tmp_path / "refined.json"
    _write_arm(baseline, {1: "Accepted", 2: "Accepted", 3: "Wrong Answer"})
    _write_arm(refined, {1: "Accepted", 2: "Wrong Answer", 3: "Wrong Answer"})
    report = analyze_historical_results(
        {"baseline_gpt35": baseline, "finetuned_refiner_gpt35": refined}
    )

    markdown = render_markdown(report)

    assert "does not demonstrate an improvement" in markdown
    assert "66.67%" in markdown
    assert "33.33%" in markdown
    assert "-33.33 pp" in markdown
    assert "Direct generation (GPT-3.5)" in markdown
    assert report.task_union_sha256 in markdown
    assert "historical judge observations" in markdown
    assert "| Arm | Derived run ID | Strategy | Historical generator |" in markdown
    assert report.arms[0].archival_run.run_id in markdown
    assert "fine-tuned prompt refinement then generation" in markdown
    assert "fine-tuned GPT-4o" in markdown
    assert "not recorded / not recorded" in markdown
    assert "exact provider snapshots or inference parameters" in markdown
    assert "or training-artifact hashes" in markdown


def test_markdown_report_uses_neutral_finding_without_named_baseline(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    _write_arm(first, {1: "Wrong Answer"})
    _write_arm(second, {1: "Accepted"})

    markdown = render_markdown(analyze_historical_results({"a": first, "b": second}))

    assert "require paired interpretation" in markdown
    assert "do not demonstrate" in markdown
