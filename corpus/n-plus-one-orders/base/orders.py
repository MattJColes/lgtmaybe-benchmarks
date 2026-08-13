def load_orders(db, users):
    ids = [user.id for user in users]
    return db.orders_for_users(ids)
