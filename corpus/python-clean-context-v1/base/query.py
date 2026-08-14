def find_user(connection, user_id: str):
    return connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
