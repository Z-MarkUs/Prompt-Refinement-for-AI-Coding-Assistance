"""OpenAI Responses API adapter loaded only for explicitly authorized live runs."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from prompt_refinement_eval.pipeline import BackendCompletion


class OpenAIResponsesBackend:
    """Minimal adapter around ``client.responses.create``."""

    def __init__(self, api_key: str, *, client: Any | None = None) -> None:
        if not api_key.strip():
            raise ValueError("api_key cannot be empty")
        if client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError(
                    "Install the optional OpenAI dependency: "
                    "pip install 'prompt-refinement-eval[openai]'"
                ) from exc
            client = OpenAI(api_key=api_key)
        self._client = client

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
        request: dict[str, object] = {
            "model": model,
            "instructions": instructions,
            "input": user_input,
            "max_output_tokens": max_output_tokens,
            "store": False,
        }
        if temperature is not None:
            request["temperature"] = temperature
        if top_p is not None:
            request["top_p"] = top_p
        create = cast(Callable[..., object], self._client.responses.create)
        response = create(**request)
        output_text = getattr(response, "output_text", "")
        if not isinstance(output_text, str) or not output_text.strip():
            raise RuntimeError("provider returned no output text")
        request_id = getattr(response, "id", None)
        response_model = getattr(response, "model", None)
        return BackendCompletion(
            text=output_text,
            request_id=request_id if isinstance(request_id, str) else None,
            response_model=response_model if isinstance(response_model, str) else None,
        )
