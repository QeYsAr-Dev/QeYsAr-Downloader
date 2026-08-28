from config import Settings


def test_hostless_runtime_paths_can_be_configured() -> None:
    configured = Settings(
        _env_file=None,
        database_path="/tmp/qeysar-downloader.db",
        temp_download_dir="/tmp/qeysar-downloads",
        log_dir="/tmp/qeysar-logs",
    )

    assert configured.database_path == (
        "/tmp/qeysar-downloader.db"
    )

    assert configured.temp_download_dir == (
        "/tmp/qeysar-downloads"
    )

    assert configured.log_dir == (
        "/tmp/qeysar-logs"
    )


def test_relative_paths_remain_supported() -> None:
    configured = Settings(
        _env_file=None,
        database_path="./downloads.db",
        temp_download_dir="./downloads",
        log_dir="./logs",
    )

    assert configured.database_path == "./downloads.db"
    assert configured.temp_download_dir == "./downloads"
    assert configured.log_dir == "./logs"
