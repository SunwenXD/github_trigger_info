import os

from discord import send_to_discord


def test_no_webhook_skips(monkeypatch):
    monkeypatch.setattr(os, "getenv", lambda k, d=None: None)
    posts = []

    def fake_post(*args, **kwargs):
        posts.append((args, kwargs))

    monkeypatch.setattr("httpx.post", fake_post)
    send_to_discord("Title", "Summary", "https://example.com")
    assert len(posts) == 0


def test_empty_webhook_skips(monkeypatch):
    monkeypatch.setattr(os, "getenv", lambda k, d=None: "")
    posts = []

    def fake_post(*args, **kwargs):
        posts.append((args, kwargs))

    monkeypatch.setattr("httpx.post", fake_post)
    send_to_discord("Title", "Summary", "https://example.com")
    assert len(posts) == 0


def test_with_webhook_sends(monkeypatch):
    monkeypatch.setattr(os, "getenv", lambda k, d=None: "https://discord.com/api/webhooks/xxx")
    posts = []

    def fake_post(url, json=None, **kwargs):
        posts.append((url, json))
        class FakeResp:
            pass
        return FakeResp()

    monkeypatch.setattr("httpx.post", fake_post)
    send_to_discord("Title", "Summary", "https://example.com")
    assert len(posts) == 1
    url, payload = posts[0]
    assert url == "https://discord.com/api/webhooks/xxx"
    assert "Title" in payload["content"]
    assert "Summary" in payload["content"]
    assert "https://example.com" in payload["content"]
