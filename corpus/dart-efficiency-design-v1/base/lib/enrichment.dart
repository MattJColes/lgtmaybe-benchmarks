Future<List<Item>> enrich(List<String> ids, Repository repository) {
  return repository.loadMany(ids);
}
