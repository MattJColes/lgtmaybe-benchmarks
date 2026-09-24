from policy import permitted

def can_export(role: str) -> bool:
    return permitted(role)
