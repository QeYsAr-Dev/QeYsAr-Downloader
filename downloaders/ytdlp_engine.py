from __future__ import annotations

import asyncio
import logging
import re
import shutil
import subprocess
import threading
import uuid

from pathlib import Path
from typing import Any, Callable

import yt_dlp

from config import settings
from downloaders.models import (
    DownloadResult,
    DownloadStatus,
    DownloadedFile,
    MediaType,
)

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[dict[str, Any]], None]


class DownloadCancelled(Exception):
    """Raised when a download is cancelled by its owner."""


class YTDLPEngine:
    """Shared yt-dlp engine with automatic format and quality handling."""

    QUALITY_LIMITS = (240, 360, 480, 720, 1080, 1440)

    def __init__(self) -> None:
        self.download_directory = settings.download_directory
        self.download_directory.mkdir(parents=True, exist_ok=True)

        self.ffmpeg_available = shutil.which("ffmpeg") is not None
        self.ffprobe_path = shutil.which("ffprobe")

    async def inspect(self, url: str) -> dict[str, Any]:
        """Inspect media metadata without downloading media bytes."""
        return await asyncio.to_thread(self._inspect_sync, url)

    @staticmethod
    def _inspect_sync(url: str) -> dict[str, Any]:
        options: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "noplaylist": False,
            "cachedir": False,
            "socket_timeout": settings.download_timeout,
            "extract_flat": False,
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)

        if not isinstance(info, dict):
            raise yt_dlp.utils.DownloadError(
                "Media information is unavailable."
            )

        return info

    @staticmethod
    def _height_value(item: dict[str, Any]) -> int | None:
        value = item.get("height")

        if value is None:
            return None

        try:
            height = int(value)
        except (TypeError, ValueError, OverflowError):
            return None

        return height if height > 0 else None

    @staticmethod
    def _width_value(item: dict[str, Any]) -> int | None:
        value = item.get("width")

        if value is None:
            return None

        try:
            width = int(value)
        except (TypeError, ValueError, OverflowError):
            return None

        return width if width > 0 else None

    @classmethod
    def _has_video(cls, item: dict[str, Any]) -> bool:
        codec = item.get("vcodec")

        if isinstance(codec, str) and codec.lower() == "none":
            return False

        if codec is not None and str(codec).strip():
            return True

        return (
            cls._height_value(item) is not None
            or cls._width_value(item) is not None
        )

    @staticmethod
    def _has_audio(item: dict[str, Any]) -> bool:
        codec = item.get("acodec")

        return (
            codec is not None
            and str(codec).strip().lower() != "none"
        )

    @classmethod
    def _height_limit(cls, max_height: int | None) -> int:
        try:
            requested_limit = (
                int(max_height)
                if max_height is not None
                else 1440
            )
        except (TypeError, ValueError, OverflowError):
            requested_limit = 1440

        if requested_limit <= 0:
            requested_limit = 1440

        requested_limit = min(requested_limit, 1440)

        allowed_limits = [
            quality
            for quality in cls.QUALITY_LIMITS
            if quality <= requested_limit
        ]

        return max(allowed_limits, default=cls.QUALITY_LIMITS[0])

    def available_qualities(
        self,
        info: dict[str, Any],
    ) -> list[int]:
        """Return known quality choices without requiring codec metadata."""
        formats = info.get("formats") or []
        heights: set[int] = set()

        for item in formats:
            if not isinstance(item, dict):
                continue

            if not self._has_video(item):
                continue

            if (
                not self.ffmpeg_available
                and item.get("acodec") == "none"
            ):
                continue

            height = self._height_value(item)

            if height is not None:
                heights.add(height)

        if self._has_video(info):
            if (
                self.ffmpeg_available
                or info.get("acodec") != "none"
            ):
                top_height = self._height_value(info)

                if top_height is not None:
                    heights.add(top_height)

        return [
            quality
            for quality in self.QUALITY_LIMITS
            if quality in heights
        ]

    def _select_format(
        self,
        info: dict[str, Any],
        max_height: int | None,
    ) -> str:
        """Build a platform-independent adaptive yt-dlp format selector."""
        height_limit = self._height_limit(max_height)
        height_filter = f"[height<=?{height_limit}]"

        formats = [
            item
            for item in (info.get("formats") or [])
            if isinstance(item, dict)
        ]

        video_formats = [
            item for item in formats if self._has_video(item)
        ]

        audio_formats = [
            item
            for item in formats
            if self._has_audio(item)
            and not self._has_video(item)
        ]

        if video_formats:
            if self.ffmpeg_available:
                return (
                    f"bv*{height_filter}+ba/"
                    f"b{height_filter}"
                )

            has_progressive_video = any(
                self._has_audio(item)
                for item in video_formats
            )

            has_unknown_audio_metadata = any(
                item.get("acodec") is None
                for item in video_formats
            )

            has_split_video = any(
                item.get("acodec") == "none"
                for item in video_formats
            )

            if (
                has_split_video
                and not has_progressive_video
                and not has_unknown_audio_metadata
            ):
                raise yt_dlp.utils.DownloadError(
                    "This media requires FFmpeg to combine "
                    "separate video and audio streams."
                )

            return f"b{height_filter}"

        if audio_formats:
            return "ba/b"

        if formats:
            return f"b{height_filter}"

        if self._has_video(info):
            if self.ffmpeg_available:
                return (
                    f"bv*{height_filter}+ba/"
                    f"b{height_filter}"
                )

            return f"b{height_filter}"

        if self._has_audio(info):
            return "ba/b"

        return f"b{height_filter}"
    async def download(
        self,
        url: str,
        platform: str,
        max_height: int | None = None,
        progress_callback: ProgressCallback | None = None,
        cancel_event: threading.Event | None = None,
    ) -> DownloadResult:
        """Download media with automatic format selection and callbacks."""
        job_directory = self.download_directory / uuid.uuid4().hex
        job_directory.mkdir(parents=True, exist_ok=True)

        cancel_event = cancel_event or threading.Event()

        if cancel_event.is_set():
            self._cleanup_directory(job_directory)

            return DownloadResult(
                success=False,
                status=DownloadStatus.CANCELLED,
                platform=platform,
                error="Download cancelled.",
            )

        try:
            info = await self.inspect(url)

            if cancel_event.is_set():
                raise DownloadCancelled(
                    "Download cancelled during inspection."
                )

            format_selector = self._select_format(
                info=info,
                max_height=max_height,
            )
            height_limit = self._height_limit(max_height)

            logger.debug(
                "Selected adaptive format selector: %s",
                format_selector,
            )

            output_template = str(
                job_directory / "%(autonumber)03d_%(title).120s.%(ext)s"
            )

            def progress_hook(data: dict[str, Any]) -> None:
                if cancel_event.is_set():
                    raise DownloadCancelled(
                        "Download cancelled by user."
                    )

                if progress_callback is not None:
                    try:
                        progress_callback(dict(data))
                    except Exception:
                        logger.debug(
                            "Download progress callback failed.",
                            exc_info=True,
                        )

            options: dict[str, Any] = {
                "outtmpl": output_template,
                "noplaylist": False,
                "quiet": True,
                "no_warnings": True,
                "restrictfilenames": True,
                "overwrites": False,
                "nooverwrites": True,
                "retries": settings.download_retries,
                "fragment_retries": settings.download_retries,
                "socket_timeout": settings.download_timeout,
                "max_filesize": settings.max_file_size_bytes,
                "format": format_selector,
                "cachedir": False,
                "nopart": False,
                "progress_hooks": [progress_hook],
            }

            worker = asyncio.create_task(
                asyncio.to_thread(
                    self._download_sync,
                    url,
                    options,
                )
            )

            try:
                downloaded_info = await asyncio.wait_for(
                    asyncio.shield(worker),
                    timeout=settings.download_timeout + 30,
                )

            except asyncio.TimeoutError:
                cancel_event.set()

                try:
                    await asyncio.wait_for(
                        asyncio.shield(worker),
                        timeout=15,
                    )
                except Exception:
                    logger.warning(
                        "Timed-out download worker did not stop cleanly."
                    )

                raise

            except asyncio.CancelledError:
                cancel_event.set()

                try:
                    await asyncio.wait_for(
                        asyncio.shield(worker),
                        timeout=15,
                    )
                except Exception:
                    logger.warning(
                        "Cancelled download worker did not stop cleanly."
                    )

                raise

            if cancel_event.is_set():
                raise DownloadCancelled(
                    "Download cancelled by user."
                )

            if not isinstance(downloaded_info, dict):
                downloaded_info = info

            files = self._collect_files(job_directory)

            if not files:
                self._cleanup_directory(job_directory)

                return DownloadResult(
                    success=False,
                    status=DownloadStatus.FAILED,
                    platform=platform,
                    error="No downloadable media was produced.",
                )

            downloaded_files: list[DownloadedFile] = []
            measured_heights: list[int] = []
            resolution_rejected = False

            for file_path in files:
                try:
                    size = file_path.stat().st_size
                except OSError:
                    continue

                if size <= 0:
                    continue

                media_type = self._detect_media_type(file_path)

                if media_type == MediaType.VIDEO:
                    actual_height = self._probe_video_height(file_path)
                    reported_height = self._reported_video_height(
                        downloaded_info
                    )

                    observed_height = (
                        actual_height
                        if actual_height is not None
                        else reported_height
                    )

                    if observed_height is not None:
                        if observed_height > height_limit:
                            logger.warning(
                                "Rejecting video above quality limit: "
                                "%s (%sp > %sp)",
                                file_path.name,
                                observed_height,
                                height_limit,
                            )

                            file_path.unlink(missing_ok=True)
                            resolution_rejected = True
                            continue

                        measured_heights.append(observed_height)

                if size > settings.max_file_size_bytes:
                    logger.warning(
                        "Rejecting oversized file: %s (%s bytes)",
                        file_path.name,
                        size,
                    )

                    file_path.unlink(missing_ok=True)
                    continue

                downloaded_files.append(
                    DownloadedFile(
                        path=str(file_path),
                        media_type=self._detect_media_type(file_path),
                        size=size,
                        title=file_path.stem,
                        extension=file_path.suffix.lower(),
                    )
                )

            if not downloaded_files:
                self._cleanup_directory(job_directory)

                error_message = (
                    f"No video was within the {height_limit}p quality limit."
                    if resolution_rejected
                    else "No file was within the 50 MB limit."
                )

                return DownloadResult(
                    success=False,
                    status=DownloadStatus.REJECTED,
                    platform=platform,
                    error=error_message,
                )

            title = (
                downloaded_info.get("title")
                or downloaded_files[0].title
            )

            selected_height = (
                max(measured_heights)
                if measured_heights
                else self._reported_video_height(downloaded_info)
            )

            return DownloadResult(
                success=True,
                status=DownloadStatus.COMPLETED,
                platform=platform,
                files=downloaded_files,
                title=str(title) if title else None,
                duration=downloaded_info.get("duration"),
                thumbnail=downloaded_info.get("thumbnail"),
                webpage_url=downloaded_info.get("webpage_url"),
                selected_height=(
                    int(selected_height)
                    if isinstance(selected_height, (int, float))
                    else None
                ),
            )

        except DownloadCancelled:
            self._cleanup_directory(job_directory)

            return DownloadResult(
                success=False,
                status=DownloadStatus.CANCELLED,
                platform=platform,
                error="Download cancelled by user.",
            )

        except asyncio.TimeoutError:
            self._cleanup_directory(job_directory)

            return DownloadResult(
                success=False,
                status=DownloadStatus.FAILED,
                platform=platform,
                error="Download timed out.",
            )

        except yt_dlp.utils.DownloadError as exc:
            self._cleanup_directory(job_directory)

            if cancel_event.is_set():
                logger.info(
                    "yt-dlp download cancelled for platform=%s",
                    platform,
                )

                return DownloadResult(
                    success=False,
                    status=DownloadStatus.CANCELLED,
                    platform=platform,
                    error="Download cancelled by user.",
                )

            logger.warning(
                "yt-dlp download failed for platform=%s: %s",
                platform,
                str(exc)[:500],
            )

            return DownloadResult(
                success=False,
                status=DownloadStatus.FAILED,
                platform=platform,
                error=self._sanitize_error(str(exc)),
            )

        except asyncio.CancelledError:
            self._cleanup_directory(job_directory)
            raise

        except Exception as exc:
            self._cleanup_directory(job_directory)

            if cancel_event.is_set():
                logger.info(
                    "Download cancelled after downloader exception for platform=%s",
                    platform,
                )

                return DownloadResult(
                    success=False,
                    status=DownloadStatus.CANCELLED,
                    platform=platform,
                    error="Download cancelled by user.",
                )

            logger.exception(
                "Unexpected downloader error for platform=%s",
                platform,
            )

            return DownloadResult(
                success=False,
                status=DownloadStatus.FAILED,
                platform=platform,
                error=self._sanitize_error(str(exc)),
            )

    @staticmethod
    def _reported_video_height(
        info: dict[str, Any],
    ) -> int | None:
        heights: list[int] = []

        top_height = YTDLPEngine._height_value(info)

        if top_height is not None:
            heights.append(top_height)

        for key in ("requested_formats", "requested_downloads"):
            items = info.get(key) or []

            for item in items:
                if not isinstance(item, dict):
                    continue

                height = YTDLPEngine._height_value(item)

                if height is None:
                    nested = item.get("info_dict")

                    if isinstance(nested, dict):
                        height = YTDLPEngine._height_value(nested)

                if height is not None:
                    heights.append(height)

        return max(heights) if heights else None

    def _probe_video_height(self, file_path: Path) -> int | None:
        """Read the actual video height when ffprobe is available."""
        if not self.ffprobe_path:
            return None

        try:
            result = subprocess.run(
                [
                    self.ffprobe_path,
                    "-v",
                    "error",
                    "-select_streams",
                    "v:0",
                    "-show_entries",
                    "stream=height",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(file_path),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=12,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            logger.debug(
                "Could not probe video dimensions: %s",
                file_path,
                exc_info=True,
            )
            return None

        if result.returncode != 0:
            return None

        for line in result.stdout.splitlines():
            try:
                height = int(line.strip())
            except (TypeError, ValueError):
                continue

            if height > 0:
                return height

        return None

    @staticmethod
    def _download_sync(
        url: str,
        options: dict[str, Any],
    ) -> dict[str, Any]:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)

        return info if isinstance(info, dict) else {}

    @staticmethod
    def _collect_files(directory: Path) -> list[Path]:
        return sorted(
            (
                path
                for path in directory.rglob("*")
                if path.is_file()
                and not path.name.endswith((".part", ".ytdl"))
            ),
            key=lambda path: path.name,
        )

    @staticmethod
    def _detect_media_type(file_path: Path) -> MediaType:
        extension = file_path.suffix.lower()

        video_extensions = {
            ".mp4",
            ".mkv",
            ".webm",
            ".mov",
            ".avi",
            ".flv",
            ".m4v",
        }

        photo_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".gif",
            ".bmp",
            ".avif",
        }

        audio_extensions = {
            ".mp3",
            ".m4a",
            ".aac",
            ".wav",
            ".ogg",
            ".opus",
            ".flac",
        }

        if extension in video_extensions:
            return MediaType.VIDEO

        if extension in photo_extensions:
            return MediaType.PHOTO

        if extension in audio_extensions:
            return MediaType.AUDIO

        return MediaType.FILE

    @staticmethod
    def _cleanup_directory(directory: Path) -> None:
        try:
            if not directory.exists():
                return

            for path in sorted(
                directory.rglob("*"),
                key=lambda item: len(item.parts),
                reverse=True,
            ):
                try:
                    if path.is_file():
                        path.unlink(missing_ok=True)
                    elif path.is_dir():
                        path.rmdir()
                except OSError:
                    pass

            try:
                directory.rmdir()
            except OSError:
                pass

        except OSError:
            logger.debug(
                "Could not clean temporary directory: %s",
                directory,
                exc_info=True,
            )

    @staticmethod
    def _sanitize_error(error: str) -> str:
        cleaned = re.sub(r"\s+", " ", error).strip()
        return cleaned[:700]

    @staticmethod
    def cleanup_result(result: DownloadResult) -> None:
        """Remove all temporary files from completed download directories."""
        parent_directories = {
            Path(downloaded_file.path).parent
            for downloaded_file in result.files
        }

        for directory in sorted(
            parent_directories,
            key=lambda path: len(path.parts),
            reverse=True,
        ):
            YTDLPEngine._cleanup_directory(directory)