package report

import (
    "reflect"
    "testing"
)

func TestRows(t *testing.T) {
    got := Render("alice", []string{"first", "second"})
    if !reflect.DeepEqual(got, []string{"first", "second"}) { t.Fatal("lost a row") }
}
