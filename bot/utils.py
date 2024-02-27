import os
import pathlib
from string import Template

ROOT_PATH = pathlib.Path.cwd()


def full_path(path: str) -> str:
    return os.path.join(ROOT_PATH, path).replace("\\", "/")


def open_file(path: str) -> str:
    file = open(full_path(path), "r", encoding="utf8")
    return file.read()


def fill_template(template_path: str, /, **kws) -> str:
    template_text = open_file(template_path)
    template = Template(template_text)
    return template.substitute(**kws)
