from pathlib import Path

from config import settings


def ensure_runtime_directories() -> None:
    settings.download_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    settings.log_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    database_parent = Path(
        settings.database_file
    ).parent

    database_parent.mkdir(
        parents=True,
        exist_ok=True,
    )
