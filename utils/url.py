from urllib.parse import urlparse


SUPPORTED_PLATFORMS = {
    "youtube": {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
    },
    "instagram": {
        "instagram.com",
        "www.instagram.com",
        "m.instagram.com",
    },
    "tiktok": {
        "tiktok.com",
        "www.tiktok.com",
        "m.tiktok.com",
        "vm.tiktok.com",
        "vt.tiktok.com",
    },
    "pinterest": {
        "pinterest.com",
        "www.pinterest.com",
        "pin.it",
    },
}


def normalize_url(url: str) -> str:
    return url.strip()


def is_valid_url(url: str) -> bool:
    url = normalize_url(url)

    if not url:
        return False

    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def get_platform(url: str) -> str | None:
    if not is_valid_url(url):
        return None

    hostname = urlparse(url).netloc.lower().split(":")[0]

    for platform, hosts in SUPPORTED_PLATFORMS.items():
        if hostname in hosts:
            return platform

    return None
