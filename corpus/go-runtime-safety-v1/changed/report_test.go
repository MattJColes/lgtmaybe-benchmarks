package report

import "testing"

func TestRenderReturnsRows(t *testing.T) {
	if Render("alice", []string{"first", "second"}) == nil { t.Fatal("nil") }
}
