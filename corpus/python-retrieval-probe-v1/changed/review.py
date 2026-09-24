from policy import export_candidate

def can_export(role: str) -> bool:
    return export_candidate(role)
