from utils.url import get_platform, is_valid_url


def test_youtube() -> None:
    assert get_platform(
        "https://youtube.com/watch?v=test"
    ) == "youtube"


def test_instagram() -> None:
    assert get_platform(
        "https://instagram.com/p/test"
    ) == "instagram"


def test_tiktok() -> None:
    assert get_platform(
        "https://tiktok.com/@user/video/123"
    ) == "tiktok"


def test_pinterest() -> None:
    assert get_platform(
        "https://pinterest.com/pin/123"
    ) == "pinterest"


def test_invalid_url() -> None:
    assert is_valid_url("") is False
    assert is_valid_url("hello") is False
    assert is_valid_url("ftp://example.com") is False


def test_unsupported_url() -> None:
    assert get_platform(
        "https://example.com/test"
    ) is None
