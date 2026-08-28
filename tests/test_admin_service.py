def test_admin_service_import() -> None:
    from services.admin_service import admin_service

    assert admin_service is not None
