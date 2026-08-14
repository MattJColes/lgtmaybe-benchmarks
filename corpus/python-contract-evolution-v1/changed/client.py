from datetime import datetime


def fetch_user(user_id: str, timeout: int) -> tuple[dict[str, object], int]:
    return ({"id": user_id, "fetched_at": datetime.utcnow()}, timeout)
