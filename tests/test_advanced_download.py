from __future__ import annotations

import threading
from pathlib import Path

import pytest
import yt_dlp

from downloaders.models import (
    DownloadResult,
    DownloadStatus,
    DownloadedFile,
    MediaType,
)
from downloaders.ytdlp_engine import YTDLPEngine
from keyboards.quality import quality_keyboard
from services.quality_selection import (
    clear_selection,
    create_selection,
    resolve_selection,
)
from services.queue_service import UserDownloadManager


@pytest.fixture
def engine() -> YTDLPEngine:
    return YTDLPEngine()


def video_format(
    height: int,
    audio_codec: str = "none",
) -> dict:
    return {
        "format_id": str(height),
        "height": height,
        "vcodec": "avc1.64001f",
        "acodec": audio_codec,
    }


def audio_format() -> dict:
    return {
        "format_id": "audio",
        "height": None,
        "vcodec": "none",
        "acodec": "mp4a.40.2",
    }


def test_available_qualities_hide_split_streams_without_ffmpeg(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = False

    info = {
        "formats": [
            video_format(480, "mp4a.40.2"),
            video_format(720),
            video_format(2160, "mp4a.40.2"),
        ]
    }

    assert engine.available_qualities(info) == [480]


def test_available_qualities_include_mergeable_streams_with_ffmpeg(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = True

    info = {
        "formats": [
            video_format(480, "mp4a.40.2"),
            video_format(720),
            video_format(1440),
            video_format(2160, "mp4a.40.2"),
        ]
    }

    assert engine.available_qualities(info) == [
        480,
        720,
        1440,
    ]


def test_quality_options_never_include_2160p(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = True

    info = {
        "formats": [
            video_format(1080, "mp4a.40.2"),
            video_format(1440, "mp4a.40.2"),
            video_format(2160, "mp4a.40.2"),
        ]
    }

    assert 2160 not in engine.available_qualities(info)


def test_format_selector_uses_ffmpeg_for_split_streams(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = True

    info = {
        "formats": [
            video_format(720),
            audio_format(),
        ]
    }

    selected = engine._select_format(info, 720)

    assert selected == (
        "bestvideo[height<=720]+bestaudio/"
        "best[height<=720]"
    )


def test_split_streams_are_rejected_without_ffmpeg(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = False

    info = {
        "formats": [
            video_format(720),
            audio_format(),
        ]
    }

    with pytest.raises(yt_dlp.utils.DownloadError):
        engine._select_format(info, 720)


def test_progressive_format_works_without_ffmpeg(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = False

    info = {
        "formats": [
            video_format(480, "mp4a.40.2"),
            video_format(720),
        ]
    }

    assert engine._select_format(info, 480) == "best[height<=480]"


def test_format_selector_respects_selected_quality(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = False

    info = {
        "formats": [
            video_format(480, "mp4a.40.2"),
            video_format(720, "mp4a.40.2"),
            video_format(1080, "mp4a.40.2"),
        ]
    }

    assert engine._select_format(info, 720) == "best[height<=720]"


def test_automatic_format_selection_is_capped_at_1440p(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = False

    info = {
        "formats": [
            video_format(1440, "mp4a.40.2"),
            video_format(2160, "mp4a.40.2"),
        ]
    }

    assert engine._select_format(info, None) == "best[height<=1440]"


def test_audio_only_content_uses_audio_selector(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = False

    info = {
        "formats": [
            audio_format(),
        ]
    }

    assert engine._select_format(info, None) == "bestaudio/best"


def test_cleanup_result_removes_entire_job_directory(
    tmp_path: Path,
) -> None:
    job_directory = tmp_path / "job-123"
    nested_directory = job_directory / "nested"

    nested_directory.mkdir(parents=True)

    media_file = job_directory / "video.mp4"
    partial_file = nested_directory / "video.mp4.part"

    media_file.write_bytes(b"media")
    partial_file.write_bytes(b"partial")

    result = DownloadResult(
        success=True,
        status=DownloadStatus.COMPLETED,
        files=[
            DownloadedFile(
                path=str(media_file),
                media_type=MediaType.VIDEO,
                size=5,
            )
        ],
    )

    YTDLPEngine.cleanup_result(result)

    assert not media_file.exists()
    assert not partial_file.exists()
    assert not job_directory.exists()


def test_cancel_requires_matching_chat_and_message() -> None:
    manager = UserDownloadManager()
    event = threading.Event()

    manager.register_cancel_event(
        user_id=100,
        event=event,
        chat_id=200,
        message_id=300,
    )

    assert not manager.cancel_download(100, 200, 301)
    assert not event.is_set()

    assert not manager.cancel_download(100, 201, 300)
    assert not event.is_set()

    assert manager.cancel_download(100, 200, 300)
    assert event.is_set()


def test_clearing_old_event_does_not_remove_new_event() -> None:
    manager = UserDownloadManager()

    old_event = threading.Event()
    new_event = threading.Event()

    manager.register_cancel_event(100, old_event, 200, 300)
    manager.register_cancel_event(100, new_event, 200, 400)

    manager.clear_cancel_event(100, old_event)

    assert manager.cancel_download(100, 200, 400)
    assert new_event.is_set()
    assert not old_event.is_set()


@pytest.mark.asyncio
async def test_quality_selection_checks_message_and_available_quality() -> None:
    user_id = 123456
    message_id = 654321

    future = create_selection(
        user_id=user_id,
        message_id=message_id,
        qualities=[480, 720],
    )

    try:
        assert not resolve_selection(
            user_id,
            message_id + 1,
            720,
        )

        assert not resolve_selection(
            user_id,
            message_id,
            1080,
        )

        assert resolve_selection(
            user_id,
            message_id,
            720,
        )

        assert await future == 720
    finally:
        clear_selection(user_id)


@pytest.mark.asyncio
async def test_quality_selection_cancel_returns_none() -> None:
    user_id = 123457
    message_id = 654322

    future = create_selection(
        user_id=user_id,
        message_id=message_id,
        qualities=[360, 480],
    )

    try:
        assert resolve_selection(
            user_id,
            message_id,
            None,
        )

        assert await future is None
    finally:
        clear_selection(user_id)


def test_quality_keyboard_does_not_duplicate_saved_quality() -> None:
    keyboard = quality_keyboard(
        qualities=[240, 360, 480],
        preferred_quality=360,
    )

    buttons = [
        button
        for row in keyboard.inline_keyboard
        for button in row
    ]

    quality_buttons = [
        button
        for button in buttons
        if button.callback_data
        and button.callback_data.startswith("quality_select:")
    ]

    callbacks = [
        button.callback_data
        for button in quality_buttons
    ]

    assert callbacks.count("quality_select:360") == 1
    assert any(
        "ذخیره‌شده" in button.text
        for button in quality_buttons
    )
    assert any(
        button.callback_data == "quality_cancel"
        for button in buttons
    )