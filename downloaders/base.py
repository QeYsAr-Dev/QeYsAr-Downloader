from abc import ABC, abstractmethod
import threading
from typing import Any, Callable

from downloaders.models import DownloadResult

ProgressCallback = Callable[[dict[str, Any]], None]


class BaseDownloader(ABC):
    platform: str

    @abstractmethod
    async def download(
        self,
        url: str,
        max_height: int | None = None,
        progress_callback: ProgressCallback | None = None,
        cancel_event: threading.Event | None = None,
    ) -> DownloadResult:
        raise NotImplementedError