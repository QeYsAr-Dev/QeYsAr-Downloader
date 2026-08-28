from pathlib import Path


def test_production_runtime_files_exist() -> None:
    required = [
        "api.py",
        "main.py",
        "config.py",
        "Dockerfile",
        "docker-compose.yml",
        "cloud-run.yaml",
        ".dockerignore",
        ".env.example",
        "requirements.txt",
    ]

    for file_name in required:
        assert Path(file_name).exists(), file_name


def test_cloud_run_container_settings() -> None:
    content = Path(
        "cloud-run.yaml"
    ).read_text(
        encoding="utf-8"
    )

    assert "containerPort: 8080" in content
    assert "timeoutSeconds: 900" in content
    assert "maxScale: \"3\"" in content
    assert "containerConcurrency: 20" in content


def test_environment_template_contains_limits() -> None:
    content = Path(
        ".env.example"
    ).read_text(
        encoding="utf-8"
    )

    assert "MAX_FILE_SIZE_MB=50" in content
    assert "DAILY_DOWNLOAD_LIMIT=10" in content
    assert "MAX_ACTIVE_DOWNLOADS_PER_USER=1" in content
    assert "WEBHOOK_SECRET=" in content


def test_docker_runtime_command() -> None:
    content = Path(
        "Dockerfile"
    ).read_text(
        encoding="utf-8"
    )

    assert "uvicorn" in content
    assert "0.0.0.0" in content
    assert "PORT:-8080" in content
