from datetime import UTC, datetime


def fetch_user(user_id: str, timeout: int = 30) -> dict[str, object]:
    """Fetch one user, returning a stable dictionary payload."""
    return {"id": user_id, "fetched_at": datetime.now(UTC), "timeout": timeout}
