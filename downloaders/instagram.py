from downloaders.base import BaseDownloader
from downloaders.models import DownloadResult
from downloaders.ytdlp_engine import YTDLPEngine


class InstagramDownloader(BaseDownloader):
    platform = "instagram"

    def __init__(self, engine: YTDLPEngine) -> None:
        self.engine = engine

    async def download(self, url: str) -> DownloadResult:
        return await self.engine.download(
            url=url,
            platform=self.platform,
        )
