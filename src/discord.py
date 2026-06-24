import httpx
import os

WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]


def send_to_discord(title: str, summary: str, url: str):
    payload = {
        "content": f"**{title}**\n\n{summary}\n\n{url}"
    }

    httpx.post(WEBHOOK, json=payload)