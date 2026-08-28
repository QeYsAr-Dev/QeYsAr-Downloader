def test_admin_handler_exports() -> None:
    from handlers.admin import (
        admin_dashboard,
        ban_user,
        broadcast_user,
        initialize_admin,
        limit_user,
        logs_handler,
        router,
        unban_user,
        unlimit_user,
    )

    assert router is not None
    assert callable(admin_dashboard)
    assert callable(ban_user)
    assert callable(unban_user)
    assert callable(limit_user)
    assert callable(unlimit_user)
    assert callable(broadcast_user)
    assert callable(logs_handler)
    assert callable(initialize_admin)
