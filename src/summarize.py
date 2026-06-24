import httpx
import os

API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are a Minecraft update analysis assistant. "
    "Read the changelog carefully and extract ALL changes accurately. "
    "Categorize them as New Features, Changes, Bug Fixes, or Technical Changes. "
    "Preserve version numbers, block/item names, and technical details. "
    "Output in Traditional Chinese. Be concise but complete."
)


def summarize(content: str):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return content

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": content,
            }
        ],
        "temperature": 0.2,
    }

    r = httpx.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    data = r.json()
    choices = data.get("choices")
    if not choices:
        return content

    return choices[0]["message"]["content"]


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    test_content = """
    Minecraft 1.20.1 is a minor update that focuses on bug fixes and performance improvements. It does not introduce any new features or content, but it addresses several issues that were present in the previous version. Some of the key fixes include:

    - Improved stability and performance
    - Fixed various crashes and bugs
    - Enhanced compatibility with mods and plugins

    Overall, Minecraft 1.20.1 is a maintenance update that aims to provide a smoother gaming experience for players.
    """

    summary = summarize(test_content)
    print(summary)