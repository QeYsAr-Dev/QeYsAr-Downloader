import pytest

from config import settings
from utils.runtime import ensure_runtime_directories


def test_runtime_configuration() -> None:
    assert settings.max_file_size_mb == 50
    assert settings.daily_download_limit == 10
    assert settings.max_active_downloads_per_user == 1


def test_runtime_directories(tmp_path, monkeypatch) -> None:
    download_dir = tmp_path / "downloads"
    log_dir = tmp_path / "logs"
    database_file = tmp_path / "data" / "bot.db"

    monkeypatch.setattr(
        settings,
        "temp_download_dir",
        str(download_dir),
    )

    monkeypatch.setattr(
        settings,
        "log_dir",
        str(log_dir),
    )

    monkeypatch.setattr(
        settings,
        "database_path",
        str(database_file),
    )

    ensure_runtime_directories()

    assert download_dir.exists()
    assert log_dir.exists()
    assert database_file.parent.exists()
