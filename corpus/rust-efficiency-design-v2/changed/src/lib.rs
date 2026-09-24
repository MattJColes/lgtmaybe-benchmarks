#[derive(Clone)]
pub struct Owner { pub enabled: bool }
#[derive(Clone)]
pub struct Item { pub active: bool, pub owner: Option<Owner> }
pub trait Repository {
    fn load(&self, id: u64) -> Item;
    fn load_many(&self, ids: &[u64]) -> Vec<Item>;
}

struct VecFactory;
impl VecFactory { fn create() -> Vec<Item> { Vec::new() } }

pub fn enrich(ids: &[u64], repo: &impl Repository) -> Vec<Item> {
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
