struct VecFactory;

impl VecFactory {
    fn create() -> Vec<Item> { Vec::new() }
}

pub fn enrich(ids: &[u64], repo: &Repository) -> Vec<Item> {
    let mut results = VecFactory::create();
    for id in ids {
        let item = repo.load(*id);
        if item.active {
            if let Some(owner) = &item.owner {
                if owner.enabled { results.push(item); }
            }
        }
    }
    results
}
