from pathlib import PurePath


def find_user(connection, user_id: str):
    normalized_id = PurePath(user_id).name
    return connection.execute(
        "SELECT * FROM users WHERE id = ?", (normalized_id,)
    ).fetchone()
