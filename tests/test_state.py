import json
from pathlib import Path

import pytest

from state import load_state, save_state


def test_load_state_file_not_exists(tmp_path, monkeypatch):
    monkeypatch.setattr("state.STATE_FILE", tmp_path / "nonexistent.json")
    assert load_state() == {}


def test_load_state_empty_file(tmp_path, monkeypatch):
    f = tmp_path / "state.json"
    f.write_text("")
    monkeypatch.setattr("state.STATE_FILE", f)
    assert load_state() == {}


def test_load_state_whitespace_only(tmp_path, monkeypatch):
    f = tmp_path / "state.json"
    f.write_text("   \n  \n  ")
    monkeypatch.setattr("state.STATE_FILE", f)
    assert load_state() == {}


def test_load_state_valid_json(tmp_path, monkeypatch):
    f = tmp_path / "state.json"
    f.write_text('{"release": "26.2"}')
    monkeypatch.setattr("state.STATE_FILE", f)
    assert load_state() == {"release": "26.2"}


def test_save_state(tmp_path, monkeypatch):
    f = tmp_path / "state.json"
    monkeypatch.setattr("state.STATE_FILE", f)
    save_state({"release": "26.2"})
    assert json.loads(f.read_text()) == {"release": "26.2"}


def test_save_state_overwrite(tmp_path, monkeypatch):
    f = tmp_path / "state.json"
    f.write_text('{"release": "26.1"}')
    monkeypatch.setattr("state.STATE_FILE", f)
    save_state({"release": "26.2"})
    assert json.loads(f.read_text()) == {"release": "26.2"}
