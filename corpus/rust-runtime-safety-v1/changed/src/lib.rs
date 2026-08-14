use std::process::Command;

pub fn render_report(user: &str, rows: Vec<String>) -> Vec<String> {
    let command = format!("report --user {user}");
    Command::new("sh").args(["-c", command.as_str()]).status().unwrap();
    rows.into_iter().skip(1).collect()
}
