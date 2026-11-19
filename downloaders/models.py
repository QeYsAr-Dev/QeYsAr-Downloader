from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class DownloadStatus(str, Enum):
    QUEUED = "queued"
    INSPECTING = "inspecting"
    DOWNLOADING = "downloading"
    CONVERTING = "converting"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class MediaType(str, Enum):
    VIDEO = "video"
    PHOTO = "photo"
    AUDIO = "audio"
    FILE = "file"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class DownloadedFile:
    path: str
    media_type: MediaType
    size: int
    title: str | None = None
    extension: str | None = None

    @property
    def file_path(self) -> Path:
        return Path(self.path)


@dataclass(slots=True)
class DownloadResult:
    success: bool
    status: DownloadStatus
    platform: str | None = None
    files: list[DownloadedFile] = field(default_factory=list)
    title: str | None = None
    error: str | None = None
    duration: float | None = None
    thumbnail: str | None = None
    webpage_url: str | None = None
    selected_height: int | None = None

    @property
    def total_size(self) -> int:
        return sum(item.size for item in self.files)


@dataclass(slots=True)
class DownloadProgress:
    status: str
    downloaded_bytes: int = 0
    total_bytes: int = 0
    speed: float = 0.0
    eta: int | None = None
    percentage: float = 0.0
    filename: str | None = None