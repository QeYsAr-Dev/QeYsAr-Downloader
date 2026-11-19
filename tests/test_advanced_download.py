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
        "bv*[height<=?720]+ba/b[height<=?720]"
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

    assert engine._select_format(info, 480) == "b[height<=?480]"


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

    assert engine._select_format(info, 720) == "b[height<=?720]"


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

    assert engine._select_format(info, None) == "b[height<=?1440]"


def test_audio_only_content_uses_audio_selector(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = False

    info = {
        "formats": [
            audio_format(),
        ]
    }

    assert engine._select_format(info, None) == "ba/b"


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

# PART 52 UNIVERSAL FORMAT TESTS

def test_pinterest_direct_format_without_codec_metadata(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = True

    item = {
        "format_id": "720p",
        "url": "https://cdn.example/video.mp4",
        "width": 1280,
        "height": 720,
    }

    assert engine._has_video(item)
    assert engine._select_format({"formats": [item]}, 720) == (
        "bv*[height<=?720]+ba/b[height<=?720]"
    )


def test_instagram_video_version_without_codec_metadata(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = True

    item = {
        "format_id": "instagram-1080",
        "ext": "mp4",
        "url": "https://cdn.example/reel.mp4",
        "width": 1080,
        "height": 1080,
    }

    assert engine._has_video(item)
    assert engine.available_qualities({"formats": [item]}) == [1080]


def test_tiktok_video_codec_without_height_is_retained(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = False

    info = {
        "formats": [
            {
                "format_id": "tiktok-bitrate",
                "ext": "mp4",
                "vcodec": "h264",
                "acodec": "aac",
                "height": None,
            }
        ]
    }

    assert engine._has_video(info["formats"][0])
    assert engine._select_format(info, 720) == "b[height<=?720]"


def test_audio_only_format_is_not_detected_as_video(
    engine: YTDLPEngine,
) -> None:
    item = audio_format()

    assert not engine._has_video(item)
    assert engine._has_audio(item)


def test_height_limit_is_clamped_to_1440p(
    engine: YTDLPEngine,
) -> None:
    assert engine._height_limit(None) == 1440
    assert engine._height_limit(1440) == 1440
    assert engine._height_limit(2160) == 1440
    assert engine._height_limit(720) == 720


def test_unknown_height_uses_optional_format_filter(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = True

    info = {
        "formats": [
            {
                "format_id": "unknown-height",
                "vcodec": "h264",
                "acodec": "none",
                "height": None,
            },
            audio_format(),
        ]
    }

    assert engine._height_value(info["formats"][0]) is None
    assert engine._select_format(info, 1080) == (
        "bv*[height<=?1080]+ba/b[height<=?1080]"
    )


def test_reported_video_height_reads_requested_formats(
    engine: YTDLPEngine,
) -> None:
    info = {
        "height": None,
        "requested_formats": [
            {"format_id": "video", "height": 1080},
            {"format_id": "audio", "height": None},
        ],
    }

    assert engine._reported_video_height(info) == 1080


def test_reported_video_height_uses_highest_requested_stream(
    engine: YTDLPEngine,
) -> None:
    info = {
        "requested_formats": [
            {"height": 720},
            {"height": 1080},
        ]
    }

    assert engine._reported_video_height(info) == 1080


def test_ffprobe_reads_actual_video_height(
    engine: YTDLPEngine,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace
    import downloaders.ytdlp_engine as engine_module

    media_file = tmp_path / "sample.mp4"
    media_file.write_bytes(b"test")
    engine.ffprobe_path = "ffprobe"

    monkeypatch.setattr(
        engine_module.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout="1080\n",
            stderr="",
        ),
    )

    assert engine._probe_video_height(media_file) == 1080


def test_ffprobe_failure_returns_none(
    engine: YTDLPEngine,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace
    import downloaders.ytdlp_engine as engine_module

    media_file = tmp_path / "sample.mp4"
    media_file.write_bytes(b"test")
    engine.ffprobe_path = "ffprobe"

    monkeypatch.setattr(
        engine_module.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=1,
            stdout="",
            stderr="invalid media",
        ),
    )

    assert engine._probe_video_height(media_file) is None

# PART 54 REAL YTDLP SELECTION TESTS

def _run_real_format_selection(
    selector: str,
    formats: list[dict],
) -> list[dict]:
    with yt_dlp.YoutubeDL({
        "quiet": True,
        "no_warnings": True,
    }) as ydl:
        return ydl._select_formats(
            formats,
            ydl.build_format_selector(selector),
        )


def test_real_selector_accepts_pinterest_format_without_codecs(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = True

    item = {
        "format_id": "pinterest-direct",
        "ext": "mp4",
        "url": "https://cdn.example/pin.mp4",
        "width": 1280,
        "height": 720,
    }

    selector = engine._select_format({"formats": [item]}, 720)
    selected = _run_real_format_selection(selector, [item])

    assert selected
    assert selected[0]["format_id"] == "pinterest-direct"


def test_real_selector_accepts_instagram_video_without_audio_codec(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = True

    item = {
        "format_id": "instagram-video-version",
        "ext": "mp4",
        "url": "https://cdn.example/reel.mp4",
        "width": 1080,
        "height": 1080,
        "acodec": "none",
    }

    selector = engine._select_format({"formats": [item]}, 1080)
    selected = _run_real_format_selection(selector, [item])

    assert selected
    assert selected[0]["format_id"] == "instagram-video-version"


def test_real_selector_accepts_tiktok_format_without_height(
    engine: YTDLPEngine,
) -> None:
    engine.ffmpeg_available = False

    item = {
        "format_id": "tiktok-progressive",
        "ext": "mp4",
        "url": "https://cdn.example/tiktok.mp4",
        "vcodec": "h264",
        "acodec": "aac",
        "height": None,
    }

    selector = engine._select_format({"formats": [item]}, 720)
    selected = _run_real_format_selection(selector, [item])

    assert selected
    assert selected[0]["format_id"] == "tiktok-progressive"
