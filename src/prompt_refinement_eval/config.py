"""Configuration with explicit, secret-safe environment handling."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass


class ConfigurationError(ValueError):
    """Raised when experiment configuration is missing or invalid."""


def _parse_optional_float(
    value: str,
    *,
    name: str,
    minimum: float,
    maximum: float,
) -> float | None:
    if value.strip().lower() == "none":
        return None
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be a number or 'none'") from exc
    if not minimum <= parsed <= maximum:
        raise ConfigurationError(f"{name} must be between {minimum:g} and {maximum:g}")
    return parsed


def _parse_max_tokens(value: str, *, name: str) -> int:
    try:
        max_tokens = int(value)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer") from exc
    if max_tokens < 1:
        raise ConfigurationError(f"{name} must be positive")
    return max_tokens


@dataclass(frozen=True, slots=True)
class ModelStageConfig:
    """Fully serialized settings for one model stage."""

    model_id: str
    temperature: float | None = 0.0
    top_p: float | None = None
    max_output_tokens: int = 2048

    def __post_init__(self) -> None:
        if not self.model_id.strip():
            raise ValueError("model_id cannot be empty")
        if isinstance(self.temperature, bool) or (
            self.temperature is not None and not 0 <= self.temperature <= 2
        ):
            raise ValueError("temperature must be between 0 and 2 or None")
        if isinstance(self.top_p, bool) or (self.top_p is not None and not 0 <= self.top_p <= 1):
            raise ValueError("top_p must be between 0 and 1 or None")
        if isinstance(self.max_output_tokens, bool) or self.max_output_tokens < 1:
            raise ValueError("max_output_tokens must be positive")


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    """Model settings for an explicitly authorized generation run."""

    run_id: str
    generator_model: str
    refiner_model: str | None = None
    generator_temperature: float | None = 0.0
    refiner_temperature: float | None = 0.0
    generator_top_p: float | None = None
    refiner_top_p: float | None = None
    generator_max_output_tokens: int = 2048
    refiner_max_output_tokens: int = 2048
    api_key_env: str = "OPENAI_API_KEY"

    def __post_init__(self) -> None:
        if not self.run_id.strip():
            raise ValueError("run_id cannot be empty")
        if not self.generator_model.strip():
            raise ValueError("generator_model cannot be empty")
        if self.refiner_model is not None and not self.refiner_model.strip():
            raise ValueError("refiner_model cannot be blank; use None when disabled")
        if not self.api_key_env.strip():
            raise ValueError("api_key_env cannot be empty")
        self.generator_stage()
        self.refiner_stage()

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> ExperimentConfig:
        """Load non-secret settings without ever returning or logging a key."""

        values = os.environ if environ is None else environ
        run_id = values.get("PROMPT_EVAL_RUN_ID", "").strip()
        if not run_id:
            raise ConfigurationError("PROMPT_EVAL_RUN_ID is required")
        generator = values.get("PROMPT_EVAL_GENERATOR_MODEL", "").strip()
        if not generator:
            raise ConfigurationError("PROMPT_EVAL_GENERATOR_MODEL is required")

        refiner = values.get("PROMPT_EVAL_REFINER_MODEL", "").strip() or None
        generator_temperature = _parse_optional_float(
            values.get("PROMPT_EVAL_GENERATOR_TEMPERATURE", "0"),
            name="PROMPT_EVAL_GENERATOR_TEMPERATURE",
            minimum=0,
            maximum=2,
        )
        refiner_temperature = _parse_optional_float(
            values.get("PROMPT_EVAL_REFINER_TEMPERATURE", "0"),
            name="PROMPT_EVAL_REFINER_TEMPERATURE",
            minimum=0,
            maximum=2,
        )
        generator_top_p = _parse_optional_float(
            values.get("PROMPT_EVAL_GENERATOR_TOP_P", "none"),
            name="PROMPT_EVAL_GENERATOR_TOP_P",
            minimum=0,
            maximum=1,
        )
        refiner_top_p = _parse_optional_float(
            values.get("PROMPT_EVAL_REFINER_TOP_P", "none"),
            name="PROMPT_EVAL_REFINER_TOP_P",
            minimum=0,
            maximum=1,
        )
        generator_max_tokens = _parse_max_tokens(
            values.get("PROMPT_EVAL_GENERATOR_MAX_OUTPUT_TOKENS", "2048"),
            name="PROMPT_EVAL_GENERATOR_MAX_OUTPUT_TOKENS",
        )
        refiner_max_tokens = _parse_max_tokens(
            values.get("PROMPT_EVAL_REFINER_MAX_OUTPUT_TOKENS", "2048"),
            name="PROMPT_EVAL_REFINER_MAX_OUTPUT_TOKENS",
        )

        return cls(
            run_id=run_id,
            generator_model=generator,
            refiner_model=refiner,
            generator_temperature=generator_temperature,
            refiner_temperature=refiner_temperature,
            generator_top_p=generator_top_p,
            refiner_top_p=refiner_top_p,
            generator_max_output_tokens=generator_max_tokens,
            refiner_max_output_tokens=refiner_max_tokens,
        )

    def generator_stage(self) -> ModelStageConfig:
        """Return the independently configured generation stage."""

        return ModelStageConfig(
            model_id=self.generator_model,
            temperature=self.generator_temperature,
            top_p=self.generator_top_p,
            max_output_tokens=self.generator_max_output_tokens,
        )

    def refiner_stage(self) -> ModelStageConfig | None:
        """Return the optional independently configured refinement stage."""

        if self.refiner_model is None:
            return None
        return ModelStageConfig(
            model_id=self.refiner_model,
            temperature=self.refiner_temperature,
            top_p=self.refiner_top_p,
            max_output_tokens=self.refiner_max_output_tokens,
        )

    def require_api_key(self, environ: Mapping[str, str] | None = None) -> str:
        """Return the configured secret or fail without embedding it in the error."""

        values = os.environ if environ is None else environ
        api_key = values.get(self.api_key_env, "").strip()
        if not api_key:
            raise ConfigurationError(f"{self.api_key_env} is required for a live model run")
        return api_key
