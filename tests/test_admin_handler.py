def test_admin_handler_import() -> None:
    from handlers.admin import (
        initialize_admin,
        router,
    )

    assert router is not None
    assert callable(initialize_admin)
