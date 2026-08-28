from pathlib import Path


def test_cloud_run_configuration_exists() -> None:
    path = Path("cloud-run.yaml")

    assert path.exists()

    content = path.read_text(
        encoding="utf-8"
    )

    assert "qeysar-downloader" in content
    assert "containerPort: 8080" in content
    assert "maxScale" in content
    assert "timeoutSeconds" in content
    assert "/ready" in content
    assert "/health" in content


def test_cloud_run_does_not_contain_real_bot_token() -> None:
    content = Path(
        "cloud-run.yaml"
    ).read_text(
        encoding="utf-8"
    )

    assert "BOT_TOKEN=" not in content
    assert "123456:ABC" not in content
