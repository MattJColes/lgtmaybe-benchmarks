pub fn open_report(root: &Path, name: &str) -> io::Result<File> {
    File::open(root.join(name))
}
