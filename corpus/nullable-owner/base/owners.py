def owner_name(record):
    owner = record.get("owner")
    return owner["name"] if owner else "unassigned"
