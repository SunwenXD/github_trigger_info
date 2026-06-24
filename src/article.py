import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.minecraft.net"
ARTICLE_INDEX = f"{BASE_URL}/en-us/article"
API_TEMPLATE = f"{BASE_URL}/content/minecraftnet/language-masters/en-us/_jcr_content.articles.page-{{}}.json"


def create_client():
    timeout = httpx.Timeout(connect=5.0, read=30.0, write=10.0, pool=5.0)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0 Safari/537.36"
        )
    }

    return httpx.Client(
        timeout=timeout,
        headers=headers,
        follow_redirects=True
    )


def fetch_json(client: httpx.Client, url: str, retries: int = 3) -> dict | None:
    last_err = None

    for _ in range(retries):
        try:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.json()
        except (httpx.ReadTimeout, httpx.HTTPError, httpx.HTTPStatusError) as e:
            last_err = e

    return None


def fetch_html(client: httpx.Client, url: str, retries: int = 3) -> str | None:
    last_err = None

    for _ in range(retries):
        try:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.text
        except (httpx.ReadTimeout, httpx.HTTPError) as e:
            last_err = e

    return None


SKIP_CATEGORIES = {"Marketplace", "Deep Dives"}

UPDATE_SLUG_KEYWORDS = [
    "snapshot", "preview", "release-candidate", "pre-release",
    "java-edition", "java-", "bedrock", "changelog",
]


def _is_update_article(slug: str) -> bool:
    slug_lower = slug.lower()
    return any(kw in slug_lower for kw in UPDATE_SLUG_KEYWORDS)


def fetch_latest_article_from_api(client: httpx.Client) -> dict | None:
    data = fetch_json(client, API_TEMPLATE.format(1))
    if not data:
        return None

    articles = data.get("article_grid", [])
    if not articles:
        return None

    candidates = []
    fallback = None

    for article in articles:
        category = article.get("primary_category", "")
        if category in SKIP_CATEGORIES:
            continue

        slug = article.get("article_url", "")
        if not slug:
            continue

        tile = article.get("default_tile") or article.get("preferred_tile")
        title = ""
        if tile:
            title = tile.get("title", "").strip()
        if not title and tile:
            title = tile.get("sub_header", "").strip()

        entry = {
            "title": title or "Minecraft Update",
            "url": urljoin(BASE_URL, slug),
            "slug": slug,
        }

        if _is_update_article(slug):
            candidates.append(entry)
        elif not fallback:
            fallback = entry

    return candidates[0] if candidates else fallback


def parse_article(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else "Minecraft Update"

    content_parts = []
    seen = set()

    article_text = soup.select_one("div.article-text div.MC_Link_Style_RichText")
    if article_text:
        for tag in article_text.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"]):
            text = tag.get_text(strip=True)
            if text and text not in seen:
                seen.add(text)
                content_parts.append(text)

    for section in soup.select("div.article-section"):
        figure = section.find("figure")
        if figure and figure.get_text(strip=True) and len(section.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5", "h6"])) <= 1:
            continue

        for tag in section.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5", "h6"]):
            text = tag.get_text(strip=True)
            if text and text not in seen:
                seen.add(text)
                content_parts.append(text)

    content = "\n".join(content_parts)

    return {
        "title": title,
        "url": url,
        "content": content
    }


def fetch_latest_article():
    with create_client() as client:
        info = fetch_latest_article_from_api(client)
        if not info:
            return None

        article_html = fetch_html(client, info["url"])
        if not article_html:
            return None

        return parse_article(article_html, info["url"])


if __name__ == "__main__":
    latest = fetch_latest_article()

    if not latest:
        print("No article found.")
    else:
        print(f"Title: {latest['title']}")
        print(f"URL: {latest['url']}")
        print("Content preview:")
        print(latest["content"][:500])

        if len(latest["content"]) > 500:
            print("\n... (truncated)")