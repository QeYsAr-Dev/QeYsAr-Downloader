import asyncio
import logging
import os
import re
import uuid
from pathlib import Path
from typing import Any

import yt_dlp

from config import settings
from downloaders.models import (
    DownloadResult,
    DownloadStatus,
    DownloadedFile,
    MediaType,
)

logger = logging.getLogger(__name__)

if os.getenv("YOUTUBE_COOKIES_CONTENT"):
    Path("/tmp/youtube_cookies.txt").write_text(
        os.getenv("YOUTUBE_COOKIES_CONTENT"),
        encoding="utf-8"
    )


class YTDLPEngine:
    """
    Shared yt-dlp based engine.

    The engine is deliberately isolated from Telegram and database
    logic so that platform-specific downloaders can reuse it.
    """

    def __init__(self) -> None:
        self.download_directory = settings.download_directory
        self.download_directory.mkdir(parents=True, exist_ok=True)

    async def download(
        self,
        url: str,
        platform: str,
    ) -> DownloadResult:
        job_id = uuid.uuid4().hex
        job_directory = self.download_directory / job_id
        job_directory.mkdir(parents=True, exist_ok=True)

        output_template = str(
            job_directory / "%(autonumber)03d_%(title).120s.%(ext)s"
        )

        options: dict[str, Any] = {
            "outtmpl": output_template,

            # Support media collections/carousels.
            "noplaylist": False,

            # Keep the console quiet; application logging handles messages.
            "quiet": True,
            "no_warnings": True,

            # File names must remain filesystem-safe.
            "restrictfilenames": True,

            # Do not overwrite files from another job.
            "overwrites": False,
            "nooverwrites": True,

            # Network reliability.
            "retries": settings.download_retries,
            "fragment_retries": settings.download_retries,
            "socket_timeout": settings.download_timeout,

            # Hard maximum size for a single remote media item.
            "max_filesize": settings.max_file_size_bytes,

            # Prefer a single downloadable file where possible.
            # This avoids requiring FFmpeg during local development.
            "format": (
                "best[filesize<=50M]/"
                "bestvideo[filesize<=50M]+bestaudio[filesize<=50M]/"
                "best"
            ),

            # Do not write yt-dlp cache into the project.
            "cachedir": False,

            # Improve YouTube compatibility with modern clients.
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web"]
                }
            },

            # Optional cookies support for blocked platforms like YouTube.
            **(
                {"cookiefile": os.getenv("YOUTUBE_COOKIES_FILE")}
                if os.getenv("YOUTUBE_COOKIES_FILE")
                else {}
            ),

            # Avoid partial leftovers where possible.
            "nopart": False,
        }

        try:
            await asyncio.wait_for(
                asyncio.to_thread(
                    self._download_sync,
                    url,
                    options,
                ),
                timeout=settings.download_timeout + 30,
            )

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

            for file_path in files:
                try:
                    size = file_path.stat().st_size
                except OSError:
                    continue

                if size <= 0:
                    continue

                if size > settings.max_file_size_bytes:
                    logger.warning(
                        "Rejecting oversized file: %s (%s bytes)",
                        file_path.name,
                        size,
                    )
                    file_path.unlink(missing_ok=True)
                    continue

                media_type = self._detect_media_type(file_path)

                downloaded_files.append(
                    DownloadedFile(
                        path=str(file_path),
                        media_type=media_type,
                        size=size,
                        title=file_path.stem,
                        extension=file_path.suffix.lower(),
                    )
                )

            if not downloaded_files:
                self._cleanup_directory(job_directory)

                return DownloadResult(
                    success=False,
                    status=DownloadStatus.REJECTED,
                    platform=platform,
                    error="All downloaded files exceeded the 50 MB limit.",
                )

            title = downloaded_files[0].title

            return DownloadResult(
                success=True,
                status=DownloadStatus.COMPLETED,
                platform=platform,
                files=downloaded_files,
                title=title,
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

        except Exception as exc:
            self._cleanup_directory(job_directory)

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
    def _download_sync(
        url: str,
        options: dict[str, Any],
    ) -> None:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

    @staticmethod
    def _collect_files(
        directory: Path,
    ) -> list[Path]:
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
    def _detect_media_type(
        file_path: Path,
    ) -> MediaType:
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
    def _cleanup_directory(
        directory: Path,
    ) -> None:
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
            pass

    @staticmethod
    def _sanitize_error(error: str) -> str:
        # Avoid returning excessively long low-level messages.
        cleaned = re.sub(r"\s+", " ", error).strip()
        return cleaned[:700]

    @staticmethod
    def cleanup_result(
        result: DownloadResult,
    ) -> None:
        """
        Remove all files produced by a download result.
        """
        for downloaded_file in result.files:
            try:
                Path(downloaded_file.path).unlink(missing_ok=True)
            except OSError:
                pass

        parent_directories: set[Path] = set()

        for downloaded_file in result.files:
            parent_directories.add(
                Path(downloaded_file.path).parent
            )

        for directory in sorted(
            parent_directories,
            key=lambda path: len(path.parts),
            reverse=True,
        ):
            try:
                directory.rmdir()
            except OSError:
                pass







