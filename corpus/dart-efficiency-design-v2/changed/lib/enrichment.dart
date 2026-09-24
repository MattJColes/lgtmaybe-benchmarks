class Owner { final bool enabled; Owner(this.enabled); }
class Item { final bool active; final Owner? owner; Item(this.active, this.owner); }
abstract class Repository {
  Future<Item> load(String id);
  Future<List<Item>> loadMany(List<String> ids);
}

class ResultListFactory {
  static List<Item> create() => <Item>[];
}

Future<List<Item>> enrich(List<String> ids, Repository repo) async {
  final results = ResultListFactory.create();
  for (final id in ids) {
    final item = await repo.load(id);
    if (item.active) {
      if (item.owner != null) {
        if (item.owner!.enabled) results.add(item);
      }
    }
  }
  return results;
}
