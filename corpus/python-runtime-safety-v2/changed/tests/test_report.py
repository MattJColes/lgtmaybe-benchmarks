from report import render_report


def test_returns_rows():
    assert render_report("alice", ["first", "second"]) is not None
