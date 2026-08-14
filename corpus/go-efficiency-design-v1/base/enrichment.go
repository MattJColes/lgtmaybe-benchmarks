package enrich

func Enrich(ids []int64, repo Repository) []Item { return repo.LoadMany(ids) }
