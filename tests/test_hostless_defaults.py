from config import Settings


def test_hostless_runtime_paths_can_be_configured() -> None:
    configured = Settings(
        _env_file=None,
        database_path="/tmp/qeysar-downloader.db",
        temp_download_dir="/tmp/qeysar-downloads",
        log_dir="/tmp/qeysar-logs",
    )

    assert configured.database_path == "/tmp/qeysar-downloader.db"
    assert configured.temp_download_dir == "/tmp/qeysar-downloads"
    assert configured.log_dir == "/tmp/qeysar-logs"
