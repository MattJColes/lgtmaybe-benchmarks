from report import render_report


def test_preserves_rows():
    assert render_report("alice", ["first", "second"]) == ["first", "second"]
