from pathlib import Path


def test_environment_template() -> None:
    content = Path(
        ".env.example"
    ).read_text(
        encoding="utf-8"
    )

    required = [
        "BOT_TOKEN=",
        "ADMIN_ID=",
        "MAX_FILE_SIZE_MB=50",
        "DAILY_DOWNLOAD_LIMIT=10",
        "MAX_ACTIVE_DOWNLOADS_PER_USER=1",
        "WEBHOOK_SECRET=",
        "PORT=8080",
        "ENVIRONMENT=production",
    ]

    for value in required:
        assert value in content
