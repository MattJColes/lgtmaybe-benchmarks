def enrich(item_ids, repository):
    results = []
    for item in repository.load_many(item_ids):
        if item.active and item.owner is not None and item.owner.enabled:
            results.append(item)
    return results
