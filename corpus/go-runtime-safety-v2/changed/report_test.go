package report

import "testing"

func TestRows(t *testing.T) {
    got := Render("alice", []string{"first", "second"})
    if got == nil { t.Fatal("missing rows") }
}
