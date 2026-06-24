import httpx
import os


def send_to_discord(title: str, summary: str, url: str):
    webhook = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook:
        return

    payload = {
        "content": f"**{title}**\n\n{summary}\n\n{url}"
    }

    httpx.post(webhook, json=payload)