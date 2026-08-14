from report import render_report


def test_render_report_preserves_rows() -> None:
    assert render_report("alice", ["first", "second"]) == ["first", "second"]
