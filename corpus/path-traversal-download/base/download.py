from pathlib import Path


def download(root, name):
    path = (root / name).resolve()
    path.relative_to(root.resolve())
    return path.read_bytes()
