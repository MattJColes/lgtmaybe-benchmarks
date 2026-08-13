def shared(left, right):
    right_set = set(right)
    return [tag for tag in left if tag in right_set]
