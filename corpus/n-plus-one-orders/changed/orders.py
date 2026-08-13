def load_orders(db, users):
    orders = []
    for user in users:
        orders.extend(db.orders_for_user(user.id))
    return orders
