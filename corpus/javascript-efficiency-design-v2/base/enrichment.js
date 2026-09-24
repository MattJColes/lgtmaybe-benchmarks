export async function enrich(ids, repo) {
  const results = [];
  for (const item of await repo.loadMany(ids)) {
    if (item.active && item.owner?.enabled) results.push(item);
  }
  return results;
}
