from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from prompt_refinement_eval.config import ModelStageConfig
from prompt_refinement_eval.pipeline import (
    BackendCompletion,
    ExperimentArm,
    PromptEvaluationPipeline,
    RunContext,
    run_arms,
    strip_markdown_fence,
)

RUN_CONTEXT = RunContext(
    run_id="run-2026-08-31-001",
    task_id="example-001",
    provider="test",
    started_at_utc="2026-08-31T00:00:00Z",
    benchmark_sha256="a" * 64,
)


def _arm(
    arm_id: str,
    generator_model: str = "generator",
    *,
    refiner_model: str | None = None,
) -> ExperimentArm:
    return ExperimentArm(
        arm_id=arm_id,
        strategy_version="test-v1",
        generator=ModelStageConfig(generator_model),
        refiner=None if refiner_model is None else ModelStageConfig(refiner_model),
    )


@dataclass
class FakeBackend:
    outputs: list[str | BackendCompletion]
    calls: list[dict[str, object]] = field(default_factory=list)

    def complete(self, **kwargs: object) -> BackendCompletion:
        self.calls.append(kwargs)
        output = self.outputs.pop(0)
        if isinstance(output, BackendCompletion):
            return output
        return BackendCompletion(
            output,
            request_id=f"request-{len(self.calls)}",
            response_model=str(kwargs["model"]),
        )


def test_direct_arm_generates_code_without_refinement() -> None:
    backend = FakeBackend(["```python\nclass Solution:\n    pass\n```"])
    pipeline = PromptEvaluationPipeline(backend)

    result = pipeline.run(
        context=RUN_CONTEXT,
        prompt="Return the sum.",
        function_signature="def add(a: int, b: int) -> int:",
        arm=_arm("direct"),
    )

    assert result.generated_code == "class Solution:\n    pass"
    assert result.effective_prompt == "Return the sum."
    assert len(backend.calls) == 1
    assert backend.calls[0]["model"] == "generator"
    assert result.generator_request_id == "request-1"
    assert result.generator_response_model == "generator"
    assert result.to_dict()["schema_version"] == "1.0"
    assert result.completed_at_utc.endswith("Z")


def test_refined_arm_uses_refiner_output_for_generation() -> None:
    backend = FakeBackend(["A precise specification", "def answer():\n    return 42"])
    pipeline = PromptEvaluationPipeline(backend)

    result = pipeline.run(
        context=RUN_CONTEXT,
        prompt="solve it",
        function_signature="def answer() -> int:",
        arm=ExperimentArm(
            arm_id="refined",
            strategy_version="refined-v1",
            refiner=ModelStageConfig(
                "refiner",
                temperature=1,
                top_p=1,
                max_output_tokens=1024,
            ),
            generator=ModelStageConfig(
                "generator",
                temperature=0,
                top_p=None,
                max_output_tokens=2048,
            ),
        ),
    )

    assert result.effective_prompt == "A precise specification"
    assert len(backend.calls) == 2
    assert backend.calls[0]["model"] == "refiner"
    assert backend.calls[0]["temperature"] == 1
    assert backend.calls[0]["top_p"] == 1
    assert backend.calls[0]["max_output_tokens"] == 1024
    assert backend.calls[1]["temperature"] == 0
    assert backend.calls[1]["top_p"] is None
    assert backend.calls[1]["max_output_tokens"] == 2048
    assert "A precise specification" in str(backend.calls[1]["user_input"])
    assert result.refinement_seconds >= 0
    assert result.generation_seconds >= 0
    serialized = result.to_dict()
    assert serialized["context"]["task_id"] == "example-001"
    assert serialized["arm_config"]["arm_id"] == "refined"
    assert serialized["arm_config"]["refiner"]["temperature"] == 1
    assert serialized["refiner_request_id"] == "request-1"
    assert serialized["generator_request_id"] == "request-2"


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "arm_id": "",
            "strategy_version": "v1",
            "generator": ModelStageConfig("generator"),
        },
        {
            "arm_id": "arm",
            "strategy_version": "",
            "generator": ModelStageConfig("generator"),
        },
    ],
)
def test_experiment_arm_rejects_invalid_configuration(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        ExperimentArm(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"run_id": ""}, "run_id"),
        ({"started_at_utc": "not-a-date"}, "ISO-8601"),
        ({"started_at_utc": "2026-08-31T08:00:00+08:00"}, "UTC"),
        ({"benchmark_sha256": "A" * 64}, "lowercase hexadecimal"),
    ],
)
def test_run_context_rejects_ambiguous_provenance(kwargs: dict[str, object], message: str) -> None:
    values: dict[str, object] = {
        "run_id": "run-1",
        "task_id": "task-1",
        "provider": "test",
        "started_at_utc": "2026-08-31T00:00:00Z",
        "benchmark_sha256": "a" * 64,
    }
    values.update(kwargs)

    with pytest.raises(ValueError, match=message):
        RunContext(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("prompt", "signature", "message"),
    [("", "def f():", "prompt"), ("task", "", "signature")],
)
def test_pipeline_rejects_empty_task_fields(prompt: str, signature: str, message: str) -> None:
    pipeline = PromptEvaluationPipeline(FakeBackend([]))
    with pytest.raises(ValueError, match=message):
        pipeline.run(
            context=RUN_CONTEXT,
            prompt=prompt,
            function_signature=signature,
            arm=_arm("direct"),
        )


def test_pipeline_rejects_empty_provider_outputs() -> None:
    refined = _arm("refined", refiner_model="refiner")
    with pytest.raises(RuntimeError, match="refiner"):
        PromptEvaluationPipeline(FakeBackend([" "])).run(
            context=RUN_CONTEXT,
            prompt="task",
            function_signature="def f():",
            arm=refined,
        )

    with pytest.raises(RuntimeError, match="generator"):
        PromptEvaluationPipeline(FakeBackend(["```\n\n```"])).run(
            context=RUN_CONTEXT,
            prompt="task",
            function_signature="def f():",
            arm=_arm("direct"),
        )


def test_run_arms_rejects_duplicate_names() -> None:
    pipeline = PromptEvaluationPipeline(FakeBackend([]))
    arms = [
        _arm("same", "a"),
        _arm("same", "b"),
    ]
    with pytest.raises(ValueError, match="unique"):
        run_arms(
            pipeline,
            context=RUN_CONTEXT,
            prompt="task",
            function_signature="def f():",
            arms=arms,
        )


def test_run_arms_requires_an_arm_and_preserves_order() -> None:
    pipeline = PromptEvaluationPipeline(FakeBackend(["first", "second"]))
    with pytest.raises(ValueError, match="at least one"):
        run_arms(
            pipeline,
            context=RUN_CONTEXT,
            prompt="task",
            function_signature="def f():",
            arms=[],
        )

    results = run_arms(
        pipeline,
        context=RUN_CONTEXT,
        prompt="task",
        function_signature="def f():",
        arms=[
            _arm("first"),
            _arm("second"),
        ],
    )
    assert [result.arm_config.arm_id for result in results] == ["first", "second"]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("plain text", "plain text"),
        ("```\nprint('x')\n```", "print('x')"),
        ("```python\nprint('x')\n```", "print('x')"),
        ("```python\nunterminated", "```python\nunterminated"),
    ],
)
def test_strip_markdown_fence(value: str, expected: str) -> None:
    assert strip_markdown_fence(value) == expected
