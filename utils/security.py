from urllib.parse import urlparse


PRIVATE_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
}


PRIVATE_SUFFIXES = (
    ".local",
    ".localhost",
    ".internal",
)


def is_safe_public_url(
    url: str,
) -> bool:
    try:
        parsed = urlparse(url)

        if parsed.scheme not in {
            "http",
            "https",
        }:
            return False

        hostname = (
            parsed.hostname or ""
        ).lower().strip()

        if not hostname:
            return False

        if hostname in PRIVATE_HOSTS:
            return False

        if hostname.endswith(
            PRIVATE_SUFFIXES
        ):
            return False

        return True

    except ValueError:
        return False
