class ResultArrayFactory {
  static create() { return []; }
}

export async function enrich(ids, repo) {
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
