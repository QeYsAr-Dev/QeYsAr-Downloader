def test_core_modules_import() -> None:
    from bot.bot import create_bot, create_dispatcher
    from database.database import init_db
    from handlers.help import router as help_router
    from handlers.history import router as history_router
    from handlers.menu import router as menu_router
    from handlers.settings import router as settings_router
    from handlers.start import router as start_router
    from handlers.stats import router as stats_router

    assert callable(create_bot)
    assert callable(create_dispatcher)
    assert callable(init_db)

    assert help_router is not None
    assert history_router is not None
    assert menu_router is not None
    assert settings_router is not None
    assert start_router is not None
    assert stats_router is not None
