import os
from pathlib import Path

from main import main


def _mock_deps(monkeypatch, tmp_path, state_content=None):
    state_file = tmp_path / "state.json"
    if state_content is not None:
        state_file.write_text(state_content)
    else:
        state_file.write_text("")

    monkeypatch.setattr("state.STATE_FILE", state_file)
    monkeypatch.setattr("version.fetch_latest_java_version", lambda: {"release": "26.2", "snapshot": "26.3-snapshot-1"})
    monkeypatch.setattr(os, "getenv", lambda k, d=None: "")


def _with_article(monkeypatch):
    monkeypatch.setattr("main.fetch_latest_article", lambda: {"title": "Test", "url": "https://example.com", "content": "Added something New"})


def _with_no_article(monkeypatch):
    monkeypatch.setattr("main.fetch_latest_article", lambda: None)


def test_same_version_skips(monkeypatch, tmp_path):
    _mock_deps(monkeypatch, tmp_path, state_content='{"release": "26.2"}')

    events = []
    monkeypatch.setattr("main.send_to_discord", lambda *a, **kw: events.append(("discord", a, kw)))
    monkeypatch.setattr("main.summarize", lambda c: c)

    main()
    assert len(events) == 0


def test_empty_state_proceeds(monkeypatch, tmp_path):
    _mock_deps(monkeypatch, tmp_path, state_content="")
    _with_article(monkeypatch)

    events = []
    monkeypatch.setattr("main.send_to_discord", lambda *a, **kw: events.append(("discord", a, kw)))
    monkeypatch.setattr("main.summarize", lambda c: c)

    main()
    state_file = tmp_path / "state.json"
    assert state_file.read_text().strip() != ""


def test_no_article_skips_discord(monkeypatch, tmp_path):
    _mock_deps(monkeypatch, tmp_path, state_content="")
    _with_no_article(monkeypatch)

    events = []
    monkeypatch.setattr("main.send_to_discord", lambda *a, **kw: events.append(("discord", a, kw)))

    main()
    assert len(events) == 0


def test_different_version_proceeds(monkeypatch, tmp_path):
    _mock_deps(monkeypatch, tmp_path, state_content='{"release": "26.1"}')
    _with_article(monkeypatch)

    events = []
    monkeypatch.setattr("main.send_to_discord", lambda *a, **kw: events.append(("discord", a, kw)))
    monkeypatch.setattr("main.summarize", lambda c: c)

    main()
    assert len(events) == 1
    title, summary, url = events[0][1]
    assert title == "Test"
    assert "Added something New" in summary


def test_state_saved_after_success(monkeypatch, tmp_path):
    _mock_deps(monkeypatch, tmp_path, state_content="")
    _with_article(monkeypatch)
    monkeypatch.setattr("main.send_to_discord", lambda *a, **kw: None)
    monkeypatch.setattr("main.summarize", lambda c: c)

    main()
    state_file = tmp_path / "state.json"
    import json
    assert json.loads(state_file.read_text()) == {"release": "26.2"}


def test_no_double_trigger(monkeypatch, tmp_path):
    _mock_deps(monkeypatch, tmp_path, state_content="")
    _with_article(monkeypatch)

    call_count = 0

    def counting_discord(*a, **kw):
        nonlocal call_count
        call_count += 1

    monkeypatch.setattr("main.send_to_discord", counting_discord)
    monkeypatch.setattr("main.summarize", lambda c: c)

    main()
    assert call_count == 1

    main()
    assert call_count == 1
