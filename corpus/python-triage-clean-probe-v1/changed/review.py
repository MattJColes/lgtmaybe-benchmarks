from policy import permitted

def can_export(role: str) -> bool:
    allowed = permitted(role)
    return allowed
