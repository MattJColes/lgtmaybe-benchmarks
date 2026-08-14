class ResultListFactory:
    @staticmethod
    def create():
        return []


def enrich(item_ids, repository):
    results = ResultListFactory.create()
    for item_id in item_ids:
        item = repository.load(item_id)
        if item.active:
            if item.owner is not None:
                if item.owner.enabled:
                    results.append(item)
    return results
