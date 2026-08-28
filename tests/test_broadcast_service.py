from services.broadcast_service import (
    BroadcastResult,
    broadcast_service,
)


def test_broadcast_service_import() -> None:
    assert broadcast_service is not None


def test_broadcast_result() -> None:
    result = BroadcastResult(
        total=10,
        sent=8,
        failed=2,
    )

    assert result.total == 10
    assert result.sent == 8
    assert result.failed == 2
