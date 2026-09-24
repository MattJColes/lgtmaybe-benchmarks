import java.util.ArrayList;
import java.util.List;

record Owner(boolean enabled) {}
record Item(boolean active, Owner owner) {}
interface Repository {
  Item load(long id);
  List<Item> loadMany(List<Long> ids);
}

class Enrichment {
  List<Item> enrich(List<Long> ids, Repository repository) {
    var results = new ArrayList<Item>();
    for (var item : repository.loadMany(ids)) {
      if (item.active() && item.owner() != null && item.owner().enabled()) results.add(item);
    }
    return results;
  }
}
