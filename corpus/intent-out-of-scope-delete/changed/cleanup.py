def purge_all(db):
    db.execute("DELETE FROM users")
