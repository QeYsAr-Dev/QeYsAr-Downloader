from dataclasses import dataclass, field
from enum import Enum


class DownloadStatus(str, Enum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


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


@dataclass(slots=True)
class DownloadResult:
    success: bool
    status: DownloadStatus
    platform: str | None = None
    files: list[DownloadedFile] = field(default_factory=list)
    title: str | None = None
    error: str | None = None
