#[derive(Clone)]
pub struct Owner { pub enabled: bool }
#[derive(Clone)]
pub struct Item { pub active: bool, pub owner: Option<Owner> }
pub trait Repository {
    fn load(&self, id: u64) -> Item;
    fn load_many(&self, ids: &[u64]) -> Vec<Item>;
}

pub fn enrich(ids: &[u64], repo: &impl Repository) -> Vec<Item> {
    repo.load_many(ids).into_iter().filter(|item| {
        item.active && item.owner.as_ref().is_some_and(|owner| owner.enabled)
    }).collect()
}
