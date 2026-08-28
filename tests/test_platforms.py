from utils.url import get_platform


def test_youtube_platforms() -> None:
    assert get_platform("https://youtube.com/watch?v=test") == "youtube"
    assert get_platform("https://www.youtube.com/watch?v=test") == "youtube"
    assert get_platform("https://youtu.be/test") == "youtube"


def test_instagram_platforms() -> None:
    assert get_platform("https://instagram.com/p/test") == "instagram"
    assert get_platform("https://www.instagram.com/reel/test") == "instagram"


def test_tiktok_platforms() -> None:
    assert get_platform("https://www.tiktok.com/@user/video/123") == "tiktok"
    assert get_platform("https://vm.tiktok.com/test") == "tiktok"


def test_pinterest_platforms() -> None:
    assert get_platform("https://www.pinterest.com/pin/123") == "pinterest"
    assert get_platform("https://pin.it/test") == "pinterest"


def test_unsupported_platform() -> None:
    assert get_platform("https://example.com/test") is None
