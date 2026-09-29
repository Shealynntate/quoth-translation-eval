"""Every test runs offline: opening any network connection fails the test that tried."""

from __future__ import annotations

import socket

import pytest


class NetworkBlocked(RuntimeError):
    pass


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def refuse(*args, **kwargs):
        raise NetworkBlocked("tests must not open network connections")

    monkeypatch.setattr(socket.socket, "connect", refuse)


class FakeClient:
    """Stands in for `GlossClient`. `answer(system, user)` returns the tool input, or raises."""

    def __init__(self, answer=None, tokens=(2500, 100)):
        self.answer = answer or (lambda system, user: {"translation": "an answer", "senses": []})
        self.tokens = tokens
        self.calls: list[tuple[str, str, str]] = []

    def ask(self, model, system, user):
        self.calls.append((model, system, user))
        return self.answer(system, user), *self.tokens


@pytest.fixture
def fake_client():
    return FakeClient
