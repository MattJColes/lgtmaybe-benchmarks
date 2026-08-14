class ResultArrayFactory {
  static create(): Item[] {
    return [];
  }
}

export async function enrich(ids: string[], repo: Repository) {
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
