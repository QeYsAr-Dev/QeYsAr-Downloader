from downloaders.base import BaseDownloader
from downloaders.instagram import InstagramDownloader
from downloaders.models import DownloadResult, DownloadStatus
from downloaders.pinterest import PinterestDownloader
from downloaders.platforms import PlatformDetector
from downloaders.tiktok import TikTokDownloader
from downloaders.youtube import YouTubeDownloader
from downloaders.ytdlp_engine import YTDLPEngine


class DownloaderManager:
    def __init__(self) -> None:
        engine = YTDLPEngine()

        self._downloaders: dict[str, BaseDownloader] = {
            "youtube": YouTubeDownloader(engine),
            "instagram": InstagramDownloader(engine),
            "tiktok": TikTokDownloader(engine),
            "pinterest": PinterestDownloader(engine),
        }

    def supported_platforms(self) -> tuple[str, ...]:
        return tuple(self._downloaders.keys())

    def get_downloader(
        self,
        url: str,
    ) -> BaseDownloader | None:
        platform = PlatformDetector.detect(url)

        if platform is None:
            return None

        return self._downloaders.get(platform)

    async def download(
        self,
        url: str,
    ) -> DownloadResult:
        platform = PlatformDetector.detect(url)

        if platform is None:
            return DownloadResult(
                success=False,
                status=DownloadStatus.FAILED,
                error="Unsupported platform.",
            )

        downloader = self._downloaders.get(platform)

        if downloader is None:
            return DownloadResult(
                success=False,
                status=DownloadStatus.FAILED,
                platform=platform,
                error="Downloader is not configured for this platform.",
            )

        return await downloader.download(url)
