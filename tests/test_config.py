from __future__ import annotations

import pytest

from prompt_refinement_eval.config import (
    ConfigurationError,
    ExperimentConfig,
    ModelStageConfig,
)


def test_config_loads_independent_non_secret_stage_settings() -> None:
    config = ExperimentConfig.from_env(
        {
            "PROMPT_EVAL_RUN_ID": "run-2026-08-31-001",
            "PROMPT_EVAL_GENERATOR_MODEL": "generator-model",
            "PROMPT_EVAL_REFINER_MODEL": "refiner-model",
            "PROMPT_EVAL_GENERATOR_TEMPERATURE": "0",
            "PROMPT_EVAL_REFINER_TEMPERATURE": "0.25",
            "PROMPT_EVAL_GENERATOR_TOP_P": "none",
            "PROMPT_EVAL_REFINER_TOP_P": "0.9",
            "PROMPT_EVAL_GENERATOR_MAX_OUTPUT_TOKENS": "1024",
            "PROMPT_EVAL_REFINER_MAX_OUTPUT_TOKENS": "512",
        }
    )

    assert config.run_id == "run-2026-08-31-001"
    assert config.generator_stage() == ModelStageConfig(
        "generator-model", temperature=0, top_p=None, max_output_tokens=1024
    )
    assert config.refiner_stage() == ModelStageConfig(
        "refiner-model", temperature=0.25, top_p=0.9, max_output_tokens=512
    )


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("PROMPT_EVAL_GENERATOR_TEMPERATURE", "not-a-number"),
        ("PROMPT_EVAL_REFINER_TEMPERATURE", "-0.1"),
        ("PROMPT_EVAL_GENERATOR_TEMPERATURE", "2.1"),
        ("PROMPT_EVAL_GENERATOR_TOP_P", "1.1"),
        ("PROMPT_EVAL_REFINER_TOP_P", "-0.1"),
        ("PROMPT_EVAL_GENERATOR_MAX_OUTPUT_TOKENS", "not-an-integer"),
        ("PROMPT_EVAL_REFINER_MAX_OUTPUT_TOKENS", "0"),
    ],
)
def test_config_rejects_invalid_values(name: str, value: str) -> None:
    environment = {
        "PROMPT_EVAL_RUN_ID": "run-1",
        "PROMPT_EVAL_GENERATOR_MODEL": "generator",
        name: value,
    }
    with pytest.raises(ConfigurationError):
        ExperimentConfig.from_env(environment)


def test_config_requires_run_id_generator_and_secret_separately() -> None:
    with pytest.raises(ConfigurationError, match="RUN_ID"):
        ExperimentConfig.from_env({})
    with pytest.raises(ConfigurationError, match="GENERATOR_MODEL"):
        ExperimentConfig.from_env({"PROMPT_EVAL_RUN_ID": "run-1"})

    config = ExperimentConfig(run_id="run-1", generator_model="generator")
    assert config.refiner_stage() is None
    with pytest.raises(ConfigurationError, match="OPENAI_API_KEY"):
        config.require_api_key({})
    assert config.require_api_key({"OPENAI_API_KEY": "local-secret"}) == "local-secret"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"model_id": ""},
        {"model_id": "model", "temperature": -0.1},
        {"model_id": "model", "temperature": 2.1},
        {"model_id": "model", "top_p": -0.1},
        {"model_id": "model", "top_p": 1.1},
        {"model_id": "model", "max_output_tokens": 0},
    ],
)
def test_model_stage_config_rejects_invalid_values(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        ModelStageConfig(**kwargs)  # type: ignore[arg-type]
