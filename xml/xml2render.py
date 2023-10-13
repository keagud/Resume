import datetime as dt
import json
import re
from itertools import chain, repeat
from pathlib import Path
from pprint import pprint
import jinja2
import sys

import argparse

from typing import TypeVar
from xmlschema import XMLSchema
from jinja2 import Environment, FileSystemLoader

DATA_DIR = Path(__file__).parent
TEMPLATES_DIR = Path(__file__).parent

schema_path = DATA_DIR.joinpath("schema.xsd")
resume_path = DATA_DIR.joinpath("resume.xml")
resume_json_path = DATA_DIR.joinpath("resume.json")


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t", "--template-file", type=Path, help="Template file to use", required=True
    )
    parser.add_argument(
        "-o", "--output-file", type=Path, help="Output destination", required=True
    )
    parser.add_argument(
        "-i",
        "--input-file",
        type=Path,
        help="XML file to read as source",
        required=True,
    )

    return parser.parse_args()


def xml_to_dict(input_xml: Path) -> dict:
    input_data = XMLSchema(schema_path).to_dict(input_xml)
    input_data = fix_newlines(input_data)

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


def normalize_whitespace(xml_content: str) -> bytes:
    normalized = re.sub(r"\s+", " ", xml_content)

    return normalized.encode("utf-8")


def fix_newlines(d):
    if isinstance(d, str):
        return re.sub(r"\s+", " ", d).strip()

    if isinstance(d, dict):
        return {k: fix_newlines(v) for k, v in d.items()}

    if isinstance(d, list):
        return [fix_newlines(i) for i in d]

    return d


def to_snake_case(s: str) -> str:
    result = []

    for i, c in enumerate(s):
        if c.isupper() and i > 0:
            result += "_"
        result += c.lower()

    return "".join(result)


def parse_date(s: str) -> dt.date:
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



if __name__ == "__main__":
    args = parse_args()

    data = xml_to_dict(args.input_file)

    environment = Environment(
        loader=FileSystemLoader(args.template_file.parent.resolve())
    )
    template = environment.get_template(args.template_file.name)

    template.globals["today"] = dt.date.today
    rendered_content = template.render(**data)

    with open(args.output_file, "w") as fp:
        fp.write(rendered_content)
