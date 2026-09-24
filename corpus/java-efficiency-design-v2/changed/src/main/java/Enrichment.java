import java.util.ArrayList;
import java.util.List;

record Owner(boolean enabled) {}
record Item(boolean active, Owner owner) {}
interface Repository {
  Item load(long id);
  List<Item> loadMany(List<Long> ids);
}

class ResultListFactory {
  static List<Item> create() { return new ArrayList<>(); }
}

class Enrichment {
  List<Item> enrich(List<Long> ids, Repository repository) {
    var results = ResultListFactory.create();
    for (var id : ids) {
      var item = repository.load(id);
      if (item.active()) {
        if (item.owner() != null) {
          if (item.owner().enabled()) results.add(item);
        }
      }
    }
    return results;
  }
}
