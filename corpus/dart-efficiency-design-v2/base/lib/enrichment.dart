class Owner { final bool enabled; Owner(this.enabled); }
class Item { final bool active; final Owner? owner; Item(this.active, this.owner); }
abstract class Repository {
  Future<Item> load(String id);
  Future<List<Item>> loadMany(List<String> ids);
}

Future<List<Item>> enrich(List<String> ids, Repository repo) async {
  final results = <Item>[];
  for (final item in await repo.loadMany(ids)) {
    if (item.active && (item.owner?.enabled ?? false)) results.add(item);
  }
  return results;
}
