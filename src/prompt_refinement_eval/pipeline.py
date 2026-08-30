"""Provider-neutral prompt-refinement and code-generation pipeline."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from time import perf_counter
from typing import Protocol

from prompt_refinement_eval.config import ModelStageConfig

REFINER_INSTRUCTIONS = """\
Rewrite the supplied coding task into a concise implementation specification.
Preserve every factual requirement and function signature. Do not invent constraints,
examples, algorithms, or expected outputs. Do not provide source code. Organize the
result as: objective, inputs, outputs, constraints, and edge cases. If information is
missing, label it as unknown instead of guessing.
"""

GENERATOR_INSTRUCTIONS = """\
Implement the supplied task in Python 3 using the required function signature.
Return only executable Python source code. Do not include Markdown fences, tests,
or prose. Prefer correctness and clarity; do not invent requirements.
"""


@dataclass(frozen=True, slots=True)
class BackendCompletion:
    """Provider response text plus stable identifiers useful for provenance."""

    text: str
    request_id: str | None = None
    response_model: str | None = None


class ChatBackend(Protocol):
    """Small backend surface that is easy to fake in tests."""

    def complete(
        self,
        *,
        model: str,
        instructions: str,
        user_input: str,
        temperature: float | None,
        top_p: float | None,
        max_output_tokens: int,
    ) -> BackendCompletion:
        """Return a text completion."""


@dataclass(frozen=True, slots=True)
class ExperimentArm:
    """One direct or refinement-assisted generation strategy."""

    arm_id: str
    strategy_version: str
    generator: ModelStageConfig
    refiner: ModelStageConfig | None = None

    def __post_init__(self) -> None:
        if not self.arm_id.strip():
            raise ValueError("arm_id cannot be empty")
        if not self.strategy_version.strip():
            raise ValueError("strategy_version cannot be empty")


@dataclass(frozen=True, slots=True)
class RunContext:
    """Caller-supplied provenance shared by every arm for one task run."""

    run_id: str
    task_id: str
    provider: str
    started_at_utc: str
    benchmark_sha256: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("run_id", self.run_id),
            ("task_id", self.task_id),
            ("provider", self.provider),
        ):
            if not value.strip():
                raise ValueError(f"{name} cannot be empty")
        try:
            started = datetime.fromisoformat(self.started_at_utc.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("started_at_utc must be an ISO-8601 timestamp") from exc
        if started.tzinfo is None or started.utcoffset() != timedelta(0):
            raise ValueError("started_at_utc must use the UTC offset")
        if self.benchmark_sha256 is not None and (
            len(self.benchmark_sha256) != 64
            or any(character not in "0123456789abcdef" for character in self.benchmark_sha256)
        ):
            raise ValueError("benchmark_sha256 must be 64 lowercase hexadecimal characters")


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """Auditable output from a single experiment arm."""

    context: RunContext
    arm_config: ExperimentArm
    original_prompt: str
    effective_prompt: str
    function_signature: str
    generated_code: str
    refiner_request_id: str | None
    generator_request_id: str | None
    refiner_response_model: str | None
    generator_response_model: str | None
    refinement_seconds: float
    generation_seconds: float
    completed_at_utc: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""

        return {"schema_version": "1.0", **asdict(self)}


def strip_markdown_fence(value: str) -> str:
    """Remove one wrapping Markdown code fence without changing inner code."""

    text = value.strip()
    if not text.startswith("```"):
        return text

    lines = text.splitlines()
    if len(lines) < 3 or not lines[-1].strip().startswith("```"):
        return text
    return "\n".join(lines[1:-1]).strip()


class PromptEvaluationPipeline:
    """Run direct and refinement-assisted generation with an injected backend."""

    def __init__(self, backend: ChatBackend) -> None:
        self._backend = backend

    def run(
        self,
        *,
        context: RunContext,
        prompt: str,
        function_signature: str,
        arm: ExperimentArm,
    ) -> GenerationResult:
        if not prompt.strip():
            raise ValueError("prompt cannot be empty")
        if not function_signature.strip():
            raise ValueError("function signature cannot be empty")

        effective_prompt = prompt.strip()
        refinement_seconds = 0.0
        refiner_request_id: str | None = None
        refiner_response_model: str | None = None
        if arm.refiner is not None:
            started = perf_counter()
            refinement = self._backend.complete(
                model=arm.refiner.model_id,
                instructions=REFINER_INSTRUCTIONS,
                user_input=effective_prompt,
                temperature=arm.refiner.temperature,
                top_p=arm.refiner.top_p,
                max_output_tokens=arm.refiner.max_output_tokens,
            )
            effective_prompt = refinement.text.strip()
            refiner_request_id = refinement.request_id
            refiner_response_model = refinement.response_model
            refinement_seconds = perf_counter() - started
            if not effective_prompt:
                raise RuntimeError("refiner returned an empty prompt")

        generation_input = _compose_generation_input(effective_prompt, function_signature)
        started = perf_counter()
        generation = self._backend.complete(
            model=arm.generator.model_id,
            instructions=GENERATOR_INSTRUCTIONS,
            user_input=generation_input,
            temperature=arm.generator.temperature,
            top_p=arm.generator.top_p,
            max_output_tokens=arm.generator.max_output_tokens,
        )
        generation_seconds = perf_counter() - started
        generated_code = strip_markdown_fence(generation.text)
        if not generated_code:
            raise RuntimeError("generator returned empty code")

        return GenerationResult(
            context=context,
            arm_config=arm,
            original_prompt=prompt.strip(),
            effective_prompt=effective_prompt,
            function_signature=function_signature.strip(),
            generated_code=generated_code,
            refiner_request_id=refiner_request_id,
            generator_request_id=generation.request_id,
            refiner_response_model=refiner_response_model,
            generator_response_model=generation.response_model,
            refinement_seconds=refinement_seconds,
            generation_seconds=generation_seconds,
            completed_at_utc=(
                datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
            ),
        )


def run_arms(
    pipeline: PromptEvaluationPipeline,
    *,
    context: RunContext,
    prompt: str,
    function_signature: str,
    arms: Sequence[ExperimentArm],
) -> tuple[GenerationResult, ...]:
    """Run a task through each arm in a deterministic caller-defined order."""

    if not arms:
        raise ValueError("at least one experiment arm is required")
    names = [arm.arm_id for arm in arms]
    if len(names) != len(set(names)):
        raise ValueError("experiment arm names must be unique")
    return tuple(
        pipeline.run(
            context=context,
            prompt=prompt,
            function_signature=function_signature,
            arm=arm,
        )
        for arm in arms
    )


def _compose_generation_input(prompt: str, function_signature: str) -> str:
    return (
        f"Task specification:\n{prompt.strip()}\n\n"
        f"Required function signature:\n{function_signature.strip()}"
    )
