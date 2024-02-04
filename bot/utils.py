import os
import pathlib

ROOT_PATH = pathlib.Path.cwd()


def full_path(path: str) -> str:
    return os.path.join(ROOT_PATH, path).replace("\\", "/")


def open_file(path: str) -> str:
    file = open(full_path(path), "r", encoding="utf8")
    return file.read()
