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


def test_under_limit_sends_one(monkeypatch):
    monkeypatch.setattr(os, "getenv", lambda k, d=None: "https://discord.com/api/webhooks/xxx")
    posts = []

    def fake_post(url, json=None, **kwargs):
        posts.append((url, json))
        class FakeResp:
            pass
        return FakeResp()

    monkeypatch.setattr("httpx.post", fake_post)
    send_to_discord("Title", "Short", "https://example.com")
    assert len(posts) == 1


def test_over_limit_splits_into_multiple(monkeypatch):
    monkeypatch.setattr(os, "getenv", lambda k, d=None: "https://discord.com/api/webhooks/xxx")
    posts = []

    def fake_post(url, json=None, **kwargs):
        posts.append((url, json))
        class FakeResp:
            pass
        return FakeResp()

    monkeypatch.setattr("httpx.post", fake_post)
    long_summary = "A" * 2500
    send_to_discord("Title", long_summary, "https://example.com")
    assert len(posts) == 2
    assert "Title" in posts[0][1]["content"]
    assert "https://example.com" in posts[0][1]["content"]
    assert len(posts[1][1]["content"]) <= 2000


def test_just_over_limit_splits(monkeypatch):
    monkeypatch.setattr(os, "getenv", lambda k, d=None: "https://discord.com/api/webhooks/xxx")
    posts = []

    def fake_post(url, json=None, **kwargs):
        posts.append((url, json))
        class FakeResp:
            pass
        return FakeResp()

    monkeypatch.setattr("httpx.post", fake_post)
    summary = "x" * 1970
    send_to_discord("Title", summary, "https://example.com")
    assert len(posts) == 2
    for _, p in posts:
        assert len(p["content"]) <= 2000
