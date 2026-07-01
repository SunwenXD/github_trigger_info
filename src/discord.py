import httpx
import os

MAX_LEN = 2000


def _send(webhook: str, text: str):
    httpx.post(webhook, json={"content": text}, timeout=10)


def send_to_discord(title: str, summary: str, url: str):
    webhook = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook:
        return

    first = f"**{title}**\n\n{summary}\n\n{url}"
    if len(first) <= MAX_LEN:
        _send(webhook, first)
        return

    # first message: title + as much summary as fits
    headroom = MAX_LEN - len(f"**{title}**\n\n") - len(f"\n\n{url}")
    part = summary[:headroom]
    # try to break at last newline
    if headroom < len(summary):
        cut = part.rfind("\n")
        if cut > 0:
            part = summary[:cut]
    first = f"**{title}**\n\n{part}\n\n{url}"
    _send(webhook, first)

    # remaining summary
    rest = summary[len(part):]
    while rest:
        _send(webhook, rest[:MAX_LEN])
        rest = rest[MAX_LEN:]