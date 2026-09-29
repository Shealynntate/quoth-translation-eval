"""The one place that talks to the API.

The request mirrors the app's, parameter for parameter: model, `max_tokens`, system prompt, a
single user message, one tool, and `tool_choice` forcing that tool. Nothing is added (no
temperature, no caching, no metadata), because any extra parameter would measure a request the
app never sends.
"""

from __future__ import annotations

import os

import anthropic

from . import paths
from .request import MAX_TOKENS, TOOL_NAME, tool_definition

KEY_NAME = "ANTHROPIC_API_KEY"


class MissingKey(RuntimeError):
    pass


class NoToolCall(RuntimeError):
    """The reply carried no tool call. The tokens were still billed, so they travel with it."""

    def __init__(self, stop_reason: str | None, input_tokens: int, output_tokens: int):
        super().__init__(f"no tool_use block in the reply (stop_reason={stop_reason})")
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


def read_api_key() -> str | None:
    """The key from the environment, else from a flat KEY=value `.env` in the repository root."""
    value = os.environ.get(KEY_NAME)
    if value:
        return value
    if not paths.ENV_FILE.exists():
        return None
    for line in paths.ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith(f"{KEY_NAME}="):
            value = line.split("=", 1)[1].strip().strip('"').strip("'")
            if value:
                return value
    return None


class GlossClient:
    def __init__(self) -> None:
        key = read_api_key()
        if key is None:
            raise MissingKey(f"{KEY_NAME} is not set in the environment or in .env")
        self._client = anthropic.Anthropic(api_key=key)
        self._tool = tool_definition()

    def ask(self, model: str, system: str, user: str) -> tuple[dict, int, int]:
        """Send one request. Returns (tool input, input tokens, output tokens)."""
        message = self._client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user}],
            tools=[self._tool],
            tool_choice={"type": "tool", "name": TOOL_NAME},
        )
        usage = message.usage
        block = next((b for b in message.content if b.type == "tool_use"), None)
        if block is None:
            raise NoToolCall(message.stop_reason, usage.input_tokens, usage.output_tokens)
        return dict(block.input), usage.input_tokens, usage.output_tokens
