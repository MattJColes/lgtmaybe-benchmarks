use std::fs::File;
use std::io;
use std::path::Path;

pub fn open_report(root: &Path, name: &str) -> io::Result<File> {
    let root = root.canonicalize()?;
    let candidate = root.join(name).canonicalize()?;
    candidate.strip_prefix(&root).map_err(|_| io::Error::from(io::ErrorKind::PermissionDenied))?;
    File::open(candidate)
}
