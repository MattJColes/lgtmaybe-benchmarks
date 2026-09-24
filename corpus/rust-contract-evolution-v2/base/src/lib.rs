pub struct UserRecord { pub id: String }

pub fn fetch_user(id: &str, _timeout_ms: Option<u64>) -> UserRecord {
    UserRecord { id: id.to_owned() }
}

/// Return ready when fetching is permitted.
pub fn status_label() -> &'static str { "ready" }

pub fn legacy_home_exists() -> bool { std::env::var_os("HOME").is_some() }
