import os
import shutil
from dataclasses import dataclass

from config import settings
from services.queue_service import download_manager


@dataclass(slots=True)
class HealthStatus:
    database_exists: bool
    download_directory_exists: bool
    log_directory_exists: bool
    disk_free_bytes: int
    active_downloads: int
    process_id: int

    @property
    def healthy(self) -> bool:
        return (
            self.database_exists
            and self.download_directory_exists
            and self.log_directory_exists
            and self.disk_free_bytes > 0
        )


class HealthService:
    def check(self) -> HealthStatus:
        settings.download_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        settings.log_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        disk = shutil.disk_usage(
            settings.download_directory
        )

        return HealthStatus(
            database_exists=settings.database_file.exists(),
            download_directory_exists=(
                settings.download_directory.exists()
            ),
            log_directory_exists=(
                settings.log_directory.exists()
            ),
            disk_free_bytes=disk.free,
            active_downloads=(
                download_manager.active_user_count()
            ),
            process_id=os.getpid(),
        )


health_service = HealthService()
