import os

from summarize import summarize


def test_no_api_key_returns_raw(monkeypatch):
    monkeypatch.setattr(os, "getenv", lambda k, d=None: None)
    content = "Added the Sulfur Cube mob"
    assert summarize(content) == content


def test_empty_api_key_returns_raw(monkeypatch):
    monkeypatch.setattr(os, "getenv", lambda k, d=None: "")
    content = "Added the Sulfur Cube mob"
    assert summarize(content) == content


def test_api_error_returns_raw(monkeypatch):
    monkeypatch.setattr(os, "getenv", lambda k, d=None: "fake-key")

    class FakeResponse:
        def json(self):
            return {"error": "invalid_api_key"}

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr("httpx.post", fake_post)
    content = "Added the Sulfur Cube mob"
    assert summarize(content) == content


def test_api_success(monkeypatch):
    monkeypatch.setattr(os, "getenv", lambda k, d=None: "fake-key")

    class FakeResponse:
        def json(self):
            return {
                "choices": [
                    {"message": {"content": "Summarized content!"}}
                ]
            }

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr("httpx.post", fake_post)
    assert summarize("Added the Sulfur Cube mob") == "Summarized content!"
