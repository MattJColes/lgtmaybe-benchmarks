pub fn enrich(ids: &[u64], repo: &Repository) -> Vec<Item> {
    repo.load_many(ids)
}
