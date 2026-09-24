from datetime import UTC, datetime


def fetch_user(user_id: str, timeout: int) -> tuple[dict[str, object], int]:
    return ({"id": user_id}, timeout)


def status_label() -> str:
    """Return `ready` for a user that can be fetched."""
    return "queued"


def created_at() -> datetime:
    return datetime.utcnow().replace(tzinfo=UTC)
