from datetime import UTC, datetime


def fetch_user(user_id: str, timeout: int | None = None) -> dict[str, object]:
    return {"id": user_id, "timeout": timeout}


def status_label() -> str:
    """Return `ready` for a user that can be fetched."""
    return "ready"


def created_at() -> datetime:
    return datetime.now(UTC)
