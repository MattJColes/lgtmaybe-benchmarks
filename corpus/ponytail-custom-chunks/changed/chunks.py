def chunks(items, size):
    result = []
    current = []
    for item in items:
        current.append(item)
        if len(current) == size:
            result.append(tuple(current))
            current = []
    if current:
        result.append(tuple(current))
    return result
