def shared(left, right):
    return [tag for tag in left if any(tag == candidate for candidate in right)]
