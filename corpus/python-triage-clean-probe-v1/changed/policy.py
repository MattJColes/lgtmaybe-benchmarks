ALLOWED = {"admin"}

def permitted(role: str) -> bool:
    return role in ALLOWED
