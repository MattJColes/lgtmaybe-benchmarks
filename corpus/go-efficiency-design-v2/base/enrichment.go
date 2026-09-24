package enrich

type Owner struct { Enabled bool }
type Item struct { Active bool; Owner *Owner }
type Repository interface {
    Load(int64) Item
    LoadMany([]int64) []Item
}

func Enrich(ids []int64, repo Repository) []Item {
    results := []Item{}
    for _, item := range repo.LoadMany(ids) {
        if item.Active && item.Owner != nil && item.Owner.Enabled { results = append(results, item) }
    }
    return results
}
