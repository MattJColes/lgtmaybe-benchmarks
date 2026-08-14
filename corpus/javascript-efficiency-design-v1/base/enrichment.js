export async function enrich(ids, repository) {
  return repository.loadMany(ids);
}
