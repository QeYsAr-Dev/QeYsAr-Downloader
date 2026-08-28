def test_download_service_import() -> None:
    from services.download_service import DownloadService

    service = DownloadService()

    assert service is not None
    assert service.manager is not None
