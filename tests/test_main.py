def test_main_import() -> None:
    import main

    assert callable(main.main)
