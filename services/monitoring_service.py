import os
from dataclasses import dataclass

from services.queue_service import download_manager


@dataclass(slots=True)
class RuntimeStats:
    active_downloads: int
    active_user_ids: list[int]
    process_pid: int
    cwd: str


class MonitoringService:
    def get_runtime_stats(self) -> RuntimeStats:
        return RuntimeStats(
            active_downloads=(
                download_manager.active_user_count()
            ),
            active_user_ids=(
                download_manager.active_user_ids()
            ),
            process_pid=os.getpid(),
            cwd=os.getcwd(),
        )


monitoring_service = MonitoringService()
