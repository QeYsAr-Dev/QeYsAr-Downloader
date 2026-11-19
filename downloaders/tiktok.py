import threading

from downloaders.base import BaseDownloader, ProgressCallback
from downloaders.models import DownloadResult
from downloaders.ytdlp_engine import YTDLPEngine


class TikTokDownloader(BaseDownloader):
    platform = "tiktok"

    def __init__(self, engine: YTDLPEngine) -> None:
        self.engine = engine

    async def download(
        self,
        url: str,
        max_height: int | None = None,
        progress_callback: ProgressCallback | None = None,
        cancel_event: threading.Event | None = None,
    ) -> DownloadResult:
        return await self.engine.download(
            url=url,
            platform=self.platform,
            max_height=max_height,
            progress_callback=progress_callback,
            cancel_event=cancel_event,
        )