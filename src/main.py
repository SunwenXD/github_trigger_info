from version import fetch_latest_java_version
from article import fetch_latest_article
from filter import filter_content
from summarize import summarize
from discord import send_to_discord
from state import load_state, save_state

from dotenv import load_dotenv
load_dotenv()

def main():
    state = load_state()
    version = fetch_latest_java_version()

    if state.get("release") == version["release"]:
        return

    article = fetch_latest_article()
    if not article:
        return

    filtered = filter_content(article["content"])
    summary = summarize(filtered)

    send_to_discord(
        article["title"],
        summary,
        article["url"],
    )

    save_state({"release": version["release"]})


if __name__ == "__main__":
    main()