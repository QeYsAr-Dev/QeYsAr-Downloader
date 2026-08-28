from services.monitoring_service import (
    monitoring_service,
)


def test_monitoring_service() -> None:
    stats = (
        monitoring_service.get_runtime_stats()
    )

    assert stats.active_downloads >= 0
    assert isinstance(
        stats.active_user_ids,
        list,
    )
    assert stats.process_pid > 0
    assert isinstance(
        stats.cwd,
        str,
    )
