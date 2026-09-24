use std::fs::File;
use std::io;
use std::path::Path;

pub fn open_report(root: &Path, name: &str) -> io::Result<File> {
    File::open(root.join(name))
}
