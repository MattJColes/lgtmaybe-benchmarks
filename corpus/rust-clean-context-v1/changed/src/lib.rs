pub fn open_report(root: &Path, name: &str) -> io::Result<File> {
    let root = root.canonicalize()?;
    let candidate = root.join(name).canonicalize()?;
    candidate.strip_prefix(&root).map_err(|_| io::ErrorKind::PermissionDenied)?;
    File::open(candidate)
}
