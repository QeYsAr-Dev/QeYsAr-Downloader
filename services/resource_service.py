import os
from dataclasses import dataclass


@dataclass(slots=True)
class ResourceSnapshot:
    process_id: int
    working_directory: str
    download_directory_size_bytes: int


class ResourceService:
    @staticmethod
    def _directory_size_bytes(path: str) -> int:
        total = 0

        if not os.path.exists(path):
            return 0

        for root, _, files in os.walk(path):
            for filename in files:
                file_path = os.path.join(
                    root,
                    filename,
                )

                try:
                    total += os.path.getsize(
                        file_path
                    )
                except OSError:
                    pass

        return total

    def snapshot(
        self,
        download_directory: str,
    ) -> ResourceSnapshot:
        return ResourceSnapshot(
            process_id=os.getpid(),
            working_directory=os.getcwd(),
            download_directory_size_bytes=(
                self._directory_size_bytes(
                    download_directory
                )
            ),
        )


resource_service = ResourceService()
