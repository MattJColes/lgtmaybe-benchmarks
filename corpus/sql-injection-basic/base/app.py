def get_user(db, user_id):
    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
