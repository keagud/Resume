import jinja2

from pathlib import Path
from typing import Final
import json

from jinja2 import FileSystemLoader, Environment, Template


BASE_PATH: Final[Path] = Path(__file__).parent


def slugify(key: str):
    return key.lower().replace("_", "-")


def get_template(
    filepath: Path = BASE_PATH.joinpath("html/resume_template.html"),
) -> Template:
    environment = Environment(loader=FileSystemLoader(filepath.parent.as_posix()))
    return environment.get_template(filepath.name)


def render_site(
    datafile: Path = BASE_PATH.joinpath("resume.json"),
    output_target: Path = BASE_PATH.joinpath("html/resume.html"),
):
    if not output_target.parent.exists():
        output_target.parent.mkdir(parents=True)

    with open(datafile, "r") as infile:
        file_data: dict = json.load(infile)

    template = get_template()
    rendered = template.render(**file_data)

    with open(output_target, "w") as outfile:
        outfile.write(rendered)

if __name__ == "__main__":
    render_site()
