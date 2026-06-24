import httpx
import os

GROQ_API_KEY = os.environ["GROQ_API_KEY"]

API_URL = "https://api.groq.com/openai/v1/chat/completions"


def summarize(content: str):
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "你是Minecraft更新分析助手，請只輸出玩家重點。"
            },
            {
                "role": "user",
                "content": content
            }
        ],
        "temperature": 0.2,
    }

    r = httpx.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    return r.json()["choices"][0]["message"]["content"]