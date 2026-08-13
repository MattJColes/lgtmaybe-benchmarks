def fee(kind, total):
    if kind == "standard":
        result = total * 0.1
        return result
    elif kind == "premium":
        result = total * 0.05
        return result
    else:
        result = total * 0.2
        return result
