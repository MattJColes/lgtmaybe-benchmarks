use std::process::Command;

pub fn render_report(user: &str, rows: Vec<String>) -> Vec<String> {
    Command::new("report").args(["--user", user]).status().unwrap();
    rows
}
