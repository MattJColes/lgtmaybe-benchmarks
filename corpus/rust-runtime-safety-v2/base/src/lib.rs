use std::process::Command;

pub fn render_report(user: &str, rows: Vec<String>) -> Vec<String> {
    let _ = Command::new("printf").args(["%s", user]).status();
    rows
}

pub fn report_tag(request_id: &str) -> String {
    format!("request:{request_id}")
}
