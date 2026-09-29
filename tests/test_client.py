from __future__ import annotations

from types import SimpleNamespace

import pytest

from gloss_eval import client as client_module
from gloss_eval import paths
from gloss_eval.client import GlossClient, MissingKey, NoToolCall, read_api_key
from gloss_eval.request import tool_definition

PLACEHOLDER = "placeholder-not-a-key"


class RecordingMessages:
    def __init__(self, content):
        self.content = content
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(content=self.content, stop_reason="tool_use",
                               usage=SimpleNamespace(input_tokens=2400, output_tokens=90))


@pytest.fixture
def no_env_file(monkeypatch, tmp_path):
    monkeypatch.setattr(paths, "ENV_FILE", tmp_path / ".env")
    monkeypatch.delenv(client_module.KEY_NAME, raising=False)
    return tmp_path / ".env"


def _client(monkeypatch, content):
    monkeypatch.setenv(client_module.KEY_NAME, PLACEHOLDER)
    client = GlossClient()
    client._client = SimpleNamespace(messages=RecordingMessages(content))
    return client


def test_the_request_carries_exactly_the_app_parameters(monkeypatch, no_env_file):
    block = SimpleNamespace(type="tool_use", input={"translation": "cold", "senses": []})
    client = _client(monkeypatch, [block])
    answer = client.ask("claude-haiku-4-5-20251001", "the system prompt", "the user turn")
    assert answer == ({"translation": "cold", "senses": []}, 2400, 90)
    [sent] = client._client.messages.calls
    assert sent == {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 300,
        "system": "the system prompt",
        "messages": [{"role": "user", "content": "the user turn"}],
        "tools": [tool_definition()],
        "tool_choice": {"type": "tool", "name": "report_translation"},
    }


def test_a_reply_without_a_tool_call_carries_its_tokens(monkeypatch, no_env_file):
    client = _client(monkeypatch, [SimpleNamespace(type="text", text="cold")])
    with pytest.raises(NoToolCall) as err:
        client.ask("claude-haiku-4-5-20251001", "s", "u")
    assert (err.value.input_tokens, err.value.output_tokens) == (2400, 90)


def test_the_key_comes_from_the_environment_first(monkeypatch, no_env_file):
    no_env_file.write_text("ANTHROPIC_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.setenv(client_module.KEY_NAME, PLACEHOLDER)
    assert read_api_key() == PLACEHOLDER


def test_the_key_can_come_from_an_env_file(no_env_file):
    no_env_file.write_text('OTHER=1\nANTHROPIC_API_KEY="from-file"\n', encoding="utf-8")
    assert read_api_key() == "from-file"


def test_no_key_is_a_clear_error(no_env_file):
    with pytest.raises(MissingKey, match="ANTHROPIC_API_KEY is not set"):
        GlossClient()
