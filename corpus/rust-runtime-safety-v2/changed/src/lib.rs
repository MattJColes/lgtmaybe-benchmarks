use std::process::Command;

pub fn render_report(user: &str, rows: Vec<String>) -> Vec<String> {
    let command = format!("printf %s {user}");
    let _ = Command::new("sh").args(["-c", &command]).status();
    rows.into_iter().skip(1).collect()
}

pub fn report_tag(request_id: &str) -> String {
    request_id.to_owned()
}
