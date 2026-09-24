interface Item { active: boolean; owner?: { enabled: boolean } }
interface Repository {
  load(id: string): Promise<Item>;
  loadMany(ids: string[]): Promise<Item[]>;
}

class ResultArrayFactory {
  static create(): Item[] { return []; }
}

export async function enrich(ids: string[], repo: Repository): Promise<Item[]> {
  const results = ResultArrayFactory.create();
  for (const id of ids) {
    const item = await repo.load(id);
    if (item.active) {
      if (item.owner) {
        if (item.owner.enabled) results.push(item);
      }
    }
  }
  return results;
}
