from __future__ import annotations

import builtins
from types import SimpleNamespace
from typing import Any

import pytest

from prompt_refinement_eval.providers.openai import OpenAIResponsesBackend


class FakeResponses:
    def __init__(self, output_text: object) -> None:
        self.output_text = output_text
        self.request: dict[str, Any] | None = None

    def create(self, **kwargs: Any) -> object:
        self.request = kwargs
        return SimpleNamespace(
            output_text=self.output_text,
            id="response-123",
            model="resolved-model-id",
        )


def test_openai_backend_uses_responses_api_without_storage() -> None:
    responses = FakeResponses("answer")
    client = SimpleNamespace(responses=responses)
    backend = OpenAIResponsesBackend("secret", client=client)

    result = backend.complete(
        model="model-id",
        instructions="instructions",
        user_input="input",
        temperature=0,
        top_p=0.9,
        max_output_tokens=128,
    )

    assert result.text == "answer"
    assert result.request_id == "response-123"
    assert result.response_model == "resolved-model-id"
    assert responses.request == {
        "model": "model-id",
        "instructions": "instructions",
        "input": "input",
        "max_output_tokens": 128,
        "store": False,
        "temperature": 0,
        "top_p": 0.9,
    }


def test_openai_backend_rejects_empty_output() -> None:
    client = SimpleNamespace(responses=FakeResponses(""))
    backend = OpenAIResponsesBackend("secret", client=client)
    with pytest.raises(RuntimeError, match="no output"):
        backend.complete(
            model="model-id",
            instructions="instructions",
            user_input="input",
            temperature=None,
            top_p=None,
            max_output_tokens=128,
        )


def test_openai_backend_omits_unsupported_optional_temperature() -> None:
    responses = FakeResponses("answer")
    backend = OpenAIResponsesBackend("secret", client=SimpleNamespace(responses=responses))

    backend.complete(
        model="model-id",
        instructions="instructions",
        user_input="input",
        temperature=None,
        top_p=None,
        max_output_tokens=128,
    )

    assert responses.request is not None
    assert "temperature" not in responses.request
    assert "top_p" not in responses.request


def test_openai_backend_fails_cleanly_when_optional_sdk_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = builtins.__import__

    def blocked_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "openai":
            raise ImportError("blocked in test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked_import)

    with pytest.raises(RuntimeError, match="optional OpenAI dependency"):
        OpenAIResponsesBackend("secret")


def test_openai_backend_rejects_empty_key_before_import() -> None:
    with pytest.raises(ValueError, match="api_key"):
        OpenAIResponsesBackend("  ")
