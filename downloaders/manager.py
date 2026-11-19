import threading
from typing import Any

from downloaders.base import BaseDownloader, ProgressCallback
from downloaders.instagram import InstagramDownloader
from downloaders.models import DownloadResult, DownloadStatus
from downloaders.pinterest import PinterestDownloader
from downloaders.platforms import PlatformDetector
from downloaders.tiktok import TikTokDownloader
from downloaders.ytdlp_engine import YTDLPEngine


class DownloaderManager:
    def __init__(self) -> None:
        self.engine = YTDLPEngine()

        self._downloaders: dict[str, BaseDownloader] = {
            "instagram": InstagramDownloader(self.engine),
            "tiktok": TikTokDownloader(self.engine),
            "pinterest": PinterestDownloader(self.engine),
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

    async def inspect(
        self,
        url: str,
    ) -> dict[str, Any]:
        platform = PlatformDetector.detect(url)

        if platform is None:
            raise ValueError("Unsupported platform.")

        return await self.engine.inspect(url)

    async def download(
        self,
        url: str,
        max_height: int | None = None,
        progress_callback: ProgressCallback | None = None,
        cancel_event: threading.Event | None = None,
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

        return await downloader.download(
            url=url,
            max_height=max_height,
            progress_callback=progress_callback,
            cancel_event=cancel_event,
        )