"""Main script for transforming XML resume specification into a given output format"""

import argparse
import datetime as dt
import re
import shutil
import subprocess
from contextlib import contextmanager
from itertools import chain, repeat
from os import chdir
from pathlib import Path
from typing import Final


from jinja2 import Environment, FileSystemLoader
from xmlschema import XMLSchema

ROOT_DIR: Final = Path(__file__).parent

ASSETS_DIR: Final = ROOT_DIR.joinpath("assets")
OUTPUT_DIR: Final = ROOT_DIR.joinpath("output")
DATA_DIR: Final = ROOT_DIR.joinpath("data")
TEMPLATES_DIR: Final = ROOT_DIR.joinpath("templates")


for p in [ROOT_DIR, ASSETS_DIR, DATA_DIR, TEMPLATES_DIR]:
    assert p.exists() and p.is_dir()

schema_path = DATA_DIR.joinpath("schema.xsd")
xml_path = DATA_DIR.joinpath("resume.xml")


@contextmanager
def in_dir(dir: Path):
    """Build utility context manager"""
    if not dir.exists() or not dir.is_dir():
        raise Exception("Invalid directory")

    original_dir = Path.cwd()

    try:
        chdir(dir)
        yield dir

    finally:
        chdir(original_dir)


def build_latex(tex_input: Path) -> Path:
    """Builds a .tex file into a pdf using xelatex."""
    if shutil.which("xelatex") is None:
        raise EnvironmentError(
            "Xelatex is a requirement to build PDFs. Please install it and ensure it is on PATH."
        )

    build_dir = OUTPUT_DIR.joinpath("_build").resolve()
    fonts_dir = ASSETS_DIR.joinpath("fonts").resolve()
    pdf_output_path = (
        OUTPUT_DIR.joinpath("pdf").joinpath(tex_input.stem).with_suffix(".pdf")
    )

    OUTPUT_DIR.joinpath("pdf").mkdir(exist_ok=True)

    # unfortunately TeX builds can't be done incrementally
    # so we need to delete any existing assets for hygene
    if build_dir.exists():
        if not build_dir.is_dir():
            raise FileExistsError(
                f"{build_dir.as_posix()} exists and is not a directory"
            )
        shutil.rmtree(build_dir)

    build_dir.mkdir()

    # copy files and set up symlinks so TeX gets the expected build context
    build_dir.joinpath("fonts").symlink_to(fonts_dir, target_is_directory=True)
    tex_path = build_dir.joinpath("input.tex").resolve()
    shutil.copy(tex_input, tex_path)

    # Shell out to xelatex for the build
    with in_dir(build_dir):
        subprocess.run("xelatex input.tex", shell=True).check_returncode()

    shutil.copy(build_dir.joinpath("input.pdf"), pdf_output_path)
    return pdf_output_path


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-f",
        "--format",
        type=str,
        choices=["html", "tex", "pdf"],
        required=True,
        help="Format for the final output file",
    )

    parser.add_argument("-o", "--output-file", type=Path, help="Output destination")
    parser.add_argument(
        "-x",
        "--xml",
        type=Path,
        help="XML file to read as source",
        default=xml_path,
    )

    return parser.parse_args()


def xml_to_dict(input_xml: Path) -> dict:
    """
    Validate the given input xml according to the schema,
    and parse it as a python dictionary.
    """
    input_data = XMLSchema(schema_path).to_dict(input_xml)
    input_data = fix_whitespace(input_data)

    def fix_case_recursive(d):
        if isinstance(d, dict):
            return {to_snake_case(k): fix_case_recursive(v) for k, v in d.items()}

        if isinstance(d, list):
            return [fix_case_recursive(i) for i in d]

        return d

    def parse_dates_recursive(d):
        if not isinstance(d, dict):
            return d

        amended = {}
        for k, v in d.items():
            if k.lower().endswith("date") or k.lower() == "since":
                v = parse_date(v)

            elif isinstance(v, dict):
                v = parse_dates_recursive(v)

            elif isinstance(v, list):
                v = [parse_dates_recursive(i) for i in v]

            amended[k] = v

        return amended

    data = parse_dates_recursive(input_data)
    data = fix_case_recursive(data)

    if not isinstance(data, dict):
        raise Exception

    return data


# Sometimes XML tooling inserts unwanted line breaks and whitespace.
# Recursively descends the tree structure to normalize whitespace/line breaks
def fix_whitespace(d):
    if isinstance(d, str):
        return re.sub(r"\s+", " ", d).strip()

    if isinstance(d, dict):
        return {k: fix_whitespace(v) for k, v in d.items()}

    if isinstance(d, list):
        return [fix_whitespace(i) for i in d]

    return d


# XML wants CamelCase, python wants snake_case
def to_snake_case(s: str) -> str:
    result = []
    for i, c in enumerate(s):
        if c.isupper() and i > 0:
            result += "_"
        result += c.lower()

    return "".join(result)


def parse_date(s: str) -> dt.date:
    """converts the various XML date representations into python Date objects"""
    non_digits = set(c for c in s if not c.isdigit())

    if len(non_digits) > 1:
        raise Exception(f"Bad date format: {s}. Only one delimiter allowed")

    elif len(non_digits) == 0:
        parts = [s]

    else:
        delimiter = non_digits.pop()
        parts = s.split(delimiter)

    if not len(parts[0]) == 4:
        raise Exception(f"Date must start with 4 digit year, {s} is not valid")

    params = dict(
        zip(["year", "month", "day"], chain((int(i) for i in parts), repeat(1)))
    )

    return dt.date(**params)


def render_template(template_type: str, input_xml: Path | None = None) -> Path:
    """Populates a template with values from XML"""
    if input_xml is None:
        input_xml = DATA_DIR.joinpath("resume.xml")

    input_data = xml_to_dict(input_xml)

    template_type = template_type.lower().strip().strip(".")
    file_suffix = f".{template_type}"

    input_data["filetype"] = template_type

    # resume-specific CSS is inserted rather than linked
    # this allows style changes without messing with general website assets
    if template_type == "html":
        css_file = ASSETS_DIR.joinpath("style.css")
        with open(css_file, "r") as fp:
            input_data["style"] = fp.read()

    template_filename = TEMPLATES_DIR.joinpath("template").with_suffix(file_suffix)
    if not template_filename.exists():
        raise FileNotFoundError(f"No template found: {template_filename}")

    environment = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

    template = environment.get_template(template_filename.name)

    template.globals["today"] = dt.date.today

    rendered_content = template.render(**input_data)

    output_dir = OUTPUT_DIR.joinpath(template_type)

    if not output_dir.exists():
        output_dir.mkdir(exist_ok=True, parents=True)

    output_file = output_dir.joinpath("resume").with_suffix(file_suffix).resolve()

    with open(output_file, "w") as fp:
        fp.write(rendered_content)

    return output_file


def cli():
    """Direct CLI interface"""
    args = parse_args()

    # only PDF requires the extra build steps
    if args.format != "pdf":
        output_file = render_template(args.format, input_xml=args.xml)

    else:
        tex_file = render_template("tex", input_xml=args.xml)
        output_file = build_latex(tex_file)

    if args.output_file:
        print(shutil.move(output_file, Path(args.output_file)))




def build_resume(template_type: str, input_xml: Path | None = None) -> Path:
    if template_type != "pdf":
        output_file = render_template(template_type, input_xml=input_xml)

    else:
        tex_file = render_template("tex", input_xml=input_xml)
        output_file = build_latex(tex_file)

    return output_file


if __name__ == "__main__":
    cli()
