from utils.url import get_platform


class PlatformDetector:
    @staticmethod
    def detect(url: str) -> str | None:
        return get_platform(url)
