import httpx

VERSION_API = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"


def fetch_latest_java_version():
    data = httpx.get(VERSION_API, timeout=10).json()

    return {
        "release": data["latest"]["release"],
        "snapshot": data["latest"]["snapshot"],
    }

if __name__ == "__main__":
    latest_versions = fetch_latest_java_version()
    print(f"Latest Release Version: {latest_versions['release']}")
    print(f"Latest Snapshot Version: {latest_versions['snapshot']}")