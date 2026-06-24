import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.minecraft.net"
ARTICLE_INDEX = f"{BASE_URL}/en-us/article"


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


def fetch_html(client: httpx.Client, url: str, retries: int = 3) -> str:
    last_err = None

    for _ in range(retries):
        try:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.text
        except (httpx.ReadTimeout, httpx.HTTPError) as e:
            last_err = e

    raise last_err


def extract_latest_article_link(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")

    # 更精準：只抓 article detail page
    links = soup.select("a[href^='/en-us/article/']")

    for a in links:
        href = a.get("href")
        if href and "/article/" in href and href != "/en-us/article":
            return urljoin(BASE_URL, href)

    return None


def parse_article(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else "Minecraft Update"

    paragraphs = soup.select("article p")
    if not paragraphs:
        paragraphs = soup.select("p")

    content = "\n".join(
        p.get_text(strip=True)
        for p in paragraphs
        if p.get_text(strip=True)
    )

    return {
        "title": title,
        "url": url,
        "content": content
    }


def fetch_latest_article():
    with create_client() as client:
        index_html = fetch_html(client, ARTICLE_INDEX)

        url = extract_latest_article_link(index_html)
        if not url:
            return None

        article_html = fetch_html(client, url)
        return parse_article(article_html, url)


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