from pathlib import PurePath


def find_user(connection, user_id: str):
    normalized_id = PurePath(user_id).name
    parameters = (normalized_id,)
    return connection.execute(
        "SELECT * FROM users WHERE id = ?", parameters
    ).fetchone()
