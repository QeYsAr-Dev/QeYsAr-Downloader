from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    bot_token: str = ""
    admin_id: int = 0

    database_path: str = "./downloads.db"

    max_file_size_mb: int = 50
    daily_download_limit: int = 10
    max_active_downloads_per_user: int = 1

    download_timeout: int = 300
    download_retries: int = 2

    temp_download_dir: str = "./downloads"
    log_dir: str = "./logs"

    rate_limit_requests: int = 5
    rate_limit_window_seconds: int = 10
    rate_limit_block_seconds: int = 30

    spam_threshold: int = 10
    spam_window_seconds: int = 30

    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_ignore_empty=True,
    )

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def database_file(self) -> Path:
        path = Path(self.database_path)

        if path.is_absolute():
            return path

        return BASE_DIR / path

    @property
    def download_directory(self) -> Path:
        path = Path(self.temp_download_dir)

        if path.is_absolute():
            return path

        return BASE_DIR / path

    @property
    def log_directory(self) -> Path:
        path = Path(self.log_dir)

        if path.is_absolute():
            return path

        return BASE_DIR / path


settings = Settings()
