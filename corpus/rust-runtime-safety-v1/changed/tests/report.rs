use app::render_report;

#[test]
fn returns_rows() {
    assert!(!render_report("alice", vec!["first".into(), "second".into()]).is_empty());
}
