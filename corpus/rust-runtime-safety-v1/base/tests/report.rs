use app::render_report;

#[test]
fn preserves_rows() {
    assert_eq!(render_report("alice", vec!["first".into(), "second".into()]), vec!["first", "second"]);
}
