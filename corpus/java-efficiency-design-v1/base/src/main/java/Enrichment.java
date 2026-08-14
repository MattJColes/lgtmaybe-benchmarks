class Enrichment {
  List<Item> enrich(List<Long> ids, Repository repository) { return repository.loadMany(ids); }
}
