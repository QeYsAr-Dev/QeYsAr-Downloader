import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

from bot.bot import create_bot, create_dispatcher
from database.database import init_db
from handlers.about import router as about_router
from handlers.admin import (
    initialize_admin,
)
from handlers.admin import router as admin_router
from handlers.download import router as download_router
from handlers.health import router as health_router
from handlers.help import router as help_router
from handlers.history import router as history_router
from handlers.menu import router as menu_router
from handlers.settings import router as settings_router
from handlers.start import router as start_router
from handlers.stats import router as stats_router
from middlewares.rate_limit import RateLimitMiddleware
from middlewares.user_security import (
    UserSecurityMiddleware,
)
from services.telegram_service import (
    configure_telegram_service,
)
from utils.logger import setup_logging
from utils.runtime import ensure_runtime_directories


logger = logging.getLogger(__name__)


bot = None
dispatcher = None


@asynccontextmanager
async def lifespan(
    application: FastAPI,
):
    global bot
    global dispatcher

    ensure_runtime_directories()
    setup_logging()

    await init_db()
    await initialize_admin()

    bot = create_bot()
    dispatcher = create_dispatcher()

    dispatcher.message.middleware(
        UserSecurityMiddleware()
    )

    dispatcher.message.middleware(
        RateLimitMiddleware()
    )

    dispatcher.include_router(
        start_router
    )
    dispatcher.include_router(
        help_router
    )
    dispatcher.include_router(
        about_router
    )
    dispatcher.include_router(
        history_router
    )
    dispatcher.include_router(
        stats_router
    )
    dispatcher.include_router(
        settings_router
    )
    dispatcher.include_router(
        health_router
    )
    dispatcher.include_router(
        admin_router
    )
    dispatcher.include_router(
        menu_router
    )
    dispatcher.include_router(
        download_router
    )

    configure_telegram_service(
        bot,
        dispatcher,
    )

    logger.info(
        "QeYsAr Downloader API started."
    )

    yield

    if bot is not None:
        await bot.session.close()

    logger.info(
        "QeYsAr Downloader API stopped."
    )


app = FastAPI(
    title="QeYsAr Downloader",
    version="1.0.0",
    lifespan=lifespan,
)


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get(
    "/",
    response_model=HealthResponse,
)
async def root() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="QeYsAr Downloader",
    )


@app.get(
    "/health",
    response_model=HealthResponse,
)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="QeYsAr Downloader",
    )


@app.get("/ready")
async def ready() -> dict[str, str]:
    return {
        "status": "ready",
    }


@app.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    x_webhook_secret: str | None = Header(
        default=None,
    ),
) -> dict[str, object]:
    expected_secret = os.getenv(
        "WEBHOOK_SECRET",
        "",
    )

    if expected_secret:
        if x_webhook_secret != expected_secret:
            raise HTTPException(
                status_code=403,
                detail="Invalid webhook secret.",
            )

    if bot is None or dispatcher is None:
        raise HTTPException(
            status_code=503,
            detail="Telegram service is not initialized.",
        )

    telegram = configure_telegram_service(
        bot,
        dispatcher,
    )

    try:
        update_data = await request.json()

        if not isinstance(
            update_data,
            dict,
        ):
            raise HTTPException(
                status_code=400,
                detail="Invalid Telegram update.",
            )

        await telegram.process_update(
            update_data
        )

        return {
            "ok": True,
        }

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Telegram webhook processing failed."
        )

        raise HTTPException(
            status_code=500,
            detail=f"Webhook processing failed: {str(exc)[:300]}",
        ) from exc
