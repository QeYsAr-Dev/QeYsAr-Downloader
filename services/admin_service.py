from database.repositories.admin import (
    get_all_user_ids,
)
from database.repositories.admins import (
    ensure_admin,
    is_admin,
)
from database.repositories.statistics import (
    get_active_users,
    get_downloads_since,
    get_platform_statistics,
    get_total_downloads,
    get_total_users,
)
from services.queue_service import download_manager


class AdminService:
    async def ensure_configured_admin(
        self,
        admin_id: int,
    ) -> None:
        if admin_id > 0:
            await ensure_admin(admin_id)

    async def is_authorized(
        self,
        user_id: int,
    ) -> bool:
        return await is_admin(user_id)

    async def get_dashboard(
        self,
    ) -> dict[str, object]:
        return {
            "total_users": await get_total_users(),
            "active_users": await get_active_users(24),
            "total_downloads": await get_total_downloads(),
            "downloads_24h": await get_downloads_since(24),
            "downloads_7d": await get_downloads_since(24 * 7),
            "downloads_30d": await get_downloads_since(24 * 30),
            "active_downloads": (
                download_manager.active_user_count()
            ),
            "active_user_ids": (
                download_manager.active_user_ids()
            ),
            "platforms": await get_platform_statistics(),
        }

    async def get_broadcast_targets(
        self,
    ) -> list[int]:
        return await get_all_user_ids(
            include_banned=False
        )


admin_service = AdminService()
