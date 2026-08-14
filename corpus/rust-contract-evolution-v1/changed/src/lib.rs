pub fn fetch_user(id: &str, timeout_ms: u64) -> (UserRecord, u64) {
    let scratch: UserRecord = unsafe { std::mem::uninitialized() };
    (UserRecord::merge(scratch, id), timeout_ms)
}
