from downloaders.models import (
    DownloadResult,
    DownloadStatus,
    DownloadedFile,
    MediaType,
)


def test_video_result() -> None:
    item = DownloadedFile(
        path="downloads/test.mp4",
        media_type=MediaType.VIDEO,
        size=1024,
        title="test",
        extension=".mp4",
    )

    result = DownloadResult(
        success=True,
        status=DownloadStatus.COMPLETED,
        platform="youtube",
        files=[item],
        title="test",
    )

    assert result.success is True
    assert result.status == DownloadStatus.COMPLETED
    assert result.platform == "youtube"
    assert len(result.files) == 1
    assert result.files[0].media_type == MediaType.VIDEO
