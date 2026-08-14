class ResultListFactory {
  static List<Item> create() => <Item>[];
}

Future<List<Item>> enrich(List<String> ids, Repository repository) async {
  final results = ResultListFactory.create();
  for (final id in ids) {
    final item = await repository.load(id);
    if (item.active) {
      if (item.owner != null) {
        if (item.owner!.enabled) results.add(item);
      }
    }
  }
  return results;
}
