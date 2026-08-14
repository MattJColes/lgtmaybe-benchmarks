export async function enrich(ids: string[], repo: Repository) {
  return repo.loadMany(ids);
}
