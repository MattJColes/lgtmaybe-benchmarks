def enrich(item_ids, repository):
    return repository.load_many(item_ids)
