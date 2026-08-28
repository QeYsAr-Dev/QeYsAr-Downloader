import logging

from utils.logger import setup_logging


def test_logging_uses_console_only() -> None:
    root_logger = logging.getLogger()

    previous_handlers = list(
        root_logger.handlers
    )

    try:
        root_logger.handlers.clear()

        setup_logging()

        handler_types = {
            type(handler).__name__
            for handler in root_logger.handlers
        }

        assert "StreamHandler" in handler_types
        assert "RotatingFileHandler" not in handler_types

    finally:
        root_logger.handlers.clear()

        root_logger.handlers.extend(
            previous_handlers
        )
