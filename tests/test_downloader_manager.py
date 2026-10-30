from downloaders.manager import DownloaderManager


def test_downloader_manager_supports_three_platforms() -> None:
    manager = DownloaderManager()

    supported = set(manager.supported_platforms())

    assert supported == {
        "instagram",
        "tiktok",
        "pinterest",
    }


def test_downloader_manager_resolves_instagram() -> None:
    manager = DownloaderManager()

    downloader = manager.get_downloader(
        "https://instagram.com/p/test"
    )

    assert downloader is not None
    assert downloader.platform == "instagram"


def test_downloader_manager_resolves_tiktok() -> None:
    manager = DownloaderManager()

    downloader = manager.get_downloader(
        "https://tiktok.com/@user/video/123"
    )

    assert downloader is not None
    assert downloader.platform == "tiktok"


def test_downloader_manager_resolves_pinterest() -> None:
    manager = DownloaderManager()

    downloader = manager.get_downloader(
        "https://pinterest.com/pin/123"
    )

    assert downloader is not None
    assert downloader.platform == "pinterest"


def test_downloader_manager_rejects_unknown_platform() -> None:
    manager = DownloaderManager()

    downloader = manager.get_downloader(
        "https://example.com/file"
    )

    assert downloader is None

def test_downloader_manager_rejects_youtube() -> None:
    manager = DownloaderManager()

    downloader = manager.get_downloader(
        "https://youtube.com/watch?v=test"
    )

    assert downloader is None
