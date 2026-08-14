/// Fetch one user while preserving the stable record return type.
pub fn fetch_user(id: &str, timeout_ms: Option<u64>) -> UserRecord {
    UserRecord::new(id, timeout_ms.unwrap_or(30_000))
}
