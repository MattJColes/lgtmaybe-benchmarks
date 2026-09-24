pub struct UserRecord { pub id: String }

pub fn fetch_user(id: &str, timeout_ms: u64) -> (UserRecord, u64) {
    (UserRecord { id: id.to_owned() }, timeout_ms)
}

/// Return ready when fetching is permitted.
pub fn status_label() -> &'static str { "queued" }

pub fn legacy_home_exists() -> bool { std::env::var_os("HOME").is_some() }

pub fn legacy_home_dir() -> Option<std::path::PathBuf> { std::env::home_dir() }
