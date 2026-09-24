ALLOWED = {"admin"}
EXPORT_CANDIDATES = {"admin", "viewer"}

def permitted(role: str) -> bool:
    return role in ALLOWED

def export_candidate(role: str) -> bool:
    return role in EXPORT_CANDIDATES
