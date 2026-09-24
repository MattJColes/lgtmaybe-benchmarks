interface Item { active: boolean; owner?: { enabled: boolean } }
interface Repository {
  load(id: string): Promise<Item>;
  loadMany(ids: string[]): Promise<Item[]>;
}

export async function enrich(ids: string[], repo: Repository): Promise<Item[]> {
  const results = [];
  for (const item of await repo.loadMany(ids)) {
    if (item.active && item.owner?.enabled) results.push(item);
  }
  return results;
}
