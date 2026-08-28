from config import settings


def test_file_size_limit() -> None:
    assert settings.max_file_size_mb == 50
    assert settings.max_file_size_bytes == 50 * 1024 * 1024


def test_daily_limit() -> None:
    assert settings.daily_download_limit == 10


def test_one_active_download_per_user() -> None:
    assert settings.max_active_downloads_per_user == 1
