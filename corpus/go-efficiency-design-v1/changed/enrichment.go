package enrich

type ResultSliceFactory struct{}

func (ResultSliceFactory) Create() []Item { return []Item{} }

func Enrich(ids []int64, repo Repository) []Item {
	results := (ResultSliceFactory{}).Create()
	for _, id := range ids {
		item := repo.Load(id)
		if item.Active {
			if item.Owner != nil {
				if item.Owner.Enabled { results = append(results, item) }
			}
		}
	}
	return results
}
