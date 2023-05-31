import jinja2

from pathlib import Path
from typing import Final
import json


BASE_PATH: Final[Path] = Path(__file__).parent


def render_site(
    datafile: Path = BASE_PATH.joinpath("resume.json"),
    output_target: Path = BASE_PATH.joinpath("html/resume.html"),
):
    if not output_target.parent.exists():
        output_target.parent.mkdir(parents=True)

    with open(datafile, "r") as infile:
        file_data: dict = json.load(infile)


    for k, v in file_data.items():
        pass


    

    pass
