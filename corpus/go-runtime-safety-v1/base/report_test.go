package report

import "testing"

func TestRenderPreservesRows(t *testing.T) {
	got := Render("alice", []string{"first", "second"})
	if len(got) != 2 || got[0] != "first" { t.Fatal(got) }
}
