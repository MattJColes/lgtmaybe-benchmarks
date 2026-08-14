from report import render_report


def test_render_report_returns_a_value() -> None:
    assert render_report("alice", ["first", "second"]) is not None
