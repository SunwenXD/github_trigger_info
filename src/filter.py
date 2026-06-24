
KEYWORDS_INCLUDE = [
    "Added", "New", "Introduced", "Now",
]

KEYWORDS_EXCLUDE = [
    "Fixed", "Technical", "API", "Data Pack", "Resource Pack"
]


def filter_content(text: str) -> str:
    lines = text.split("\n")

    result = []

    for line in lines:
        if any(k in line for k in KEYWORDS_EXCLUDE):
            continue

        if any(k in line for k in KEYWORDS_INCLUDE):
            result.append(line)

    return "\n".join(result)[:12000]