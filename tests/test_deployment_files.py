from pathlib import Path


def test_production_files() -> None:
    required_files = [
        "Dockerfile",
        "docker-compose.yml",
        ".dockerignore",
        ".env.example",
        "cloud-run.yaml",
        "deploy/README.md",
        "scripts/set-webhook.ps1",
        "scripts/delete-webhook.ps1",
        "scripts/run-production.ps1",
    ]

    for file_name in required_files:
        assert Path(file_name).exists(), file_name


def test_dockerfile_uses_port_environment() -> None:
    content = Path(
        "Dockerfile"
    ).read_text(
        encoding="utf-8"
    )

    assert "PORT:-8080" in content
    assert "0.0.0.0" in content
    assert "uvicorn" in content
