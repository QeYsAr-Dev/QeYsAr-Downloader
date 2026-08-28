def test_download_handler_import() -> None:
    from handlers.download import router

    assert router is not None


def test_menu_handler_import() -> None:
    from handlers.menu import router

    assert router is not None
