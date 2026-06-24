import json
from urllib.parse import urljoin

import pytest

from article import (
    fetch_latest_article_from_api,
    SKIP_CATEGORIES,
    UPDATE_SLUG_KEYWORDS,
    _is_update_article,
    parse_article,
)


SAMPLE_GRID = [
    {"default_tile": {"title": "Marketplace Promo"}, "primary_category": "Marketplace", "article_url": "/en-us/article/marketplace-promo"},
    {"default_tile": {"title": "Deep Dive Feature"}, "primary_category": "Deep Dives", "article_url": "/en-us/article/deep-dive"},
    {"default_tile": {"title": "Minecraft Snapshot 1"}, "primary_category": "News", "article_url": "/en-us/article/minecraft-snapshot-1"},
    {"default_tile": {"title": "Minecraft Preview 1.2"}, "primary_category": "", "article_url": "/en-us/article/minecraft-preview-1-2"},
    {"default_tile": {"title": "Minecraft Java Edition 26.2"}, "primary_category": "News", "article_url": "/en-us/article/minecraft-java-edition-26-2"},
    {"default_tile": {"title": "Community Event"}, "primary_category": "News", "article_url": "/en-us/article/community-event"},
    {"default_tile": {"title": ""}, "primary_category": "", "article_url": "/en-us/article/minecraft-preview-26-40-27"},
]


def test_skip_categories():
    assert "Marketplace" in SKIP_CATEGORIES
    assert "Deep Dives" in SKIP_CATEGORIES


def test_is_update_article():
    assert _is_update_article("/en-us/article/minecraft-snapshot-1") is True
    assert _is_update_article("/en-us/article/minecraft-preview-1-2") is True
    assert _is_update_article("/en-us/article/minecraft-26-2-release-candidate-2") is True
    assert _is_update_article("/en-us/article/minecraft-26-2-pre-release-6") is True
    assert _is_update_article("/en-us/article/minecraft-java-edition-26-2") is True
    assert _is_update_article("/en-us/article/minecraft-26-30-bedrock-changelog") is True
    assert _is_update_article("/en-us/article/java-26-2") is True
    assert _is_update_article("/en-us/article/community-event") is False
    assert _is_update_article("/en-us/article/choose-your-chaos") is False


def test_fetch_no_data(monkeypatch):
    monkeypatch.setattr("article.fetch_json", lambda c, u: None)
    assert fetch_latest_article_from_api(None) is None


def test_fetch_empty_grid(monkeypatch):
    monkeypatch.setattr("article.fetch_json", lambda c, u: {"article_grid": []})
    assert fetch_latest_article_from_api(None) is None


def test_fetch_prefers_update_articles(monkeypatch):
    monkeypatch.setattr("article.fetch_json", lambda c, u: {"article_grid": SAMPLE_GRID})
    result = fetch_latest_article_from_api(None)
    assert result is not None
    assert "snapshot" in result["slug"] or "preview" in result["slug"] or "java" in result["slug"]


def test_fetch_skips_marketplace(monkeypatch):
    grid = [{"default_tile": {"title": "Only Market"}, "primary_category": "Marketplace", "article_url": "/en-us/article/market"}]
    monkeypatch.setattr("article.fetch_json", lambda c, u: {"article_grid": grid})
    assert fetch_latest_article_from_api(None) is None


def test_fetch_skips_deep_dives(monkeypatch):
    grid = [{"default_tile": {"title": "Only Deep"}, "primary_category": "Deep Dives", "article_url": "/en-us/article/deep"}]
    monkeypatch.setattr("article.fetch_json", lambda c, u: {"article_grid": grid})
    assert fetch_latest_article_from_api(None) is None


def test_fetch_fallback_non_update(monkeypatch):
    grid = [
        {"default_tile": {"title": "Some News"}, "primary_category": "News", "article_url": "/en-us/article/some-news"},
        {"default_tile": {"title": "Market"}, "primary_category": "Marketplace", "article_url": "/en-us/article/market"},
    ]
    monkeypatch.setattr("article.fetch_json", lambda c, u: {"article_grid": grid})
    result = fetch_latest_article_from_api(None)
    assert result is not None
    assert result["slug"] == "/en-us/article/some-news"


def test_fetch_title_fallback_from_sub_header(monkeypatch):
    grid = [{"default_tile": {"title": "", "sub_header": "A Minecraft: Bedrock Edition Preview"}, "primary_category": "", "article_url": "/en-us/article/minecraft-preview-26-40-27"}]
    monkeypatch.setattr("article.fetch_json", lambda c, u: {"article_grid": grid})
    result = fetch_latest_article_from_api(None)
    assert result is not None
    assert result["title"] == "A Minecraft: Bedrock Edition Preview"


def test_parse_article_finds_content():
    html = """
    <html><head><title>Minecraft Update</title></head>
    <body>
    <div class="article-text"><div class="MC_Link_Style_RichText"><p>Intro text</p></div></div>
    <div class="article-section"><p>Section one content</p></div>
    <div class="article-section"><figure><img src="x.jpg"/><figcaption>Image caption</figcaption></figure></div>
    <div class="article-section"><p>Section two content</p><h2>Heading</h2></div>
    </body></html>
    """
    result = parse_article(html, "https://example.com/article")
    assert result["title"] == "Minecraft Update"
    assert result["url"] == "https://example.com/article"
    assert "Intro text" in result["content"]
    assert "Section one content" in result["content"]
    assert "Section two content" in result["content"]
    assert "Heading" in result["content"]
    assert "Image caption" not in result["content"]


def test_parse_article_dedup():
    html = """
    <html><head><title>Test</title></head>
    <body>
    <div class="article-text"><div class="MC_Link_Style_RichText"><p>Dup text</p></div></div>
    <div class="article-section"><p>Dup text</p></div>
    </body></html>
    """
    result = parse_article(html, "https://example.com")
    assert result["content"].count("Dup text") == 1


def test_parse_article_no_content():
    html = "<html><head><title>Test</title></head><body></body></html>"
    result = parse_article(html, "https://example.com")
    assert result["content"] == ""
