from pathlib import Path


def cleanup_file(file_path: str | None) -> None:
    if not file_path:
        return

    path = Path(file_path)

    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass
