from abc import ABC, abstractmethod

from downloaders.models import DownloadResult


class BaseDownloader(ABC):
    platform: str

    @abstractmethod
    async def download(self, url: str) -> DownloadResult:
        raise NotImplementedError
