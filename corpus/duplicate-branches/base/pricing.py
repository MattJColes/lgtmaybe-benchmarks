def fee(kind, total):
    rate = {"standard": 0.1, "premium": 0.05}.get(kind, 0.2)
    return total * rate
