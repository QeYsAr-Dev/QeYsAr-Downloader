from config import Settings


def test_default_runtime_paths_are_hostless_safe() -> None:
    settings = Settings(
        _env_file=None
    )

    assert settings.database_path == (
        "/tmp/qeysar-downloader.db"
    )

    assert settings.temp_download_dir == (
        "/tmp/qeysar-downloads"
    )

    assert settings.log_dir == (
        "/tmp/qeysar-logs"
    )
