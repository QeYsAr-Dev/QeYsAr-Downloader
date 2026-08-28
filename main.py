import asyncio
import logging
import os

import uvicorn

from api import app
from utils.logger import setup_logging


def main() -> None:
    setup_logging()

    logger = logging.getLogger(
        "qeysar.main"
    )

    host = "0.0.0.0"

    port = int(
        os.getenv(
            "PORT",
            "8080",
        )
    )

    logger.info(
        "Starting QeYsAr Downloader API on %s:%s",
        host,
        port,
    )

    uvicorn.run(
        app,
        host=host,
        port=port,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
