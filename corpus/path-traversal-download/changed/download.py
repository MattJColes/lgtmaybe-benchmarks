from pathlib import Path


def download(root, name):
    path = Path(root) / name
    return path.read_bytes()
