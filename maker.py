import toml, argparse, json
from functools import reduce

# parser = argparse.ArgumentParser()

# parser.add_argument('input')
# parser.add_argument('-o', '--output')
# args = parser.parse_args()

IN_FILE = "resume.toml"
OUT_FILE = "resume-toml.md"

with open(IN_FILE, "r") as infile:
    toml_data = toml.load(infile)

# print(json.dumps(toml_data, indent=4))


def toml_parse(data, level=0, indent=" ", list_item=False) -> list[str]:

    md_lines: list[str] = []
    level, prefix = (level, "-") if list_item else (level + 1, "")

    if type(data) is dict:
        for header, subdata in data.items():
            md_lines.append(("#" * level) + " " + header)
            md_lines.extend(toml_parse(subdata, level=level, indent=indent))

    elif type(data) is list:
        md_lines = reduce(
            lambda a, b: a + b,
            [toml_parse(d, level=level, indent=indent, list_item=True) for d in data],
        )

    else:
        md_lines.append((indent * level) + prefix + str(data))

    return md_lines


#########################
def toml_parsde(data, level=0, indent=" ", prefix="-") -> list[str]:

    if not (isinstance(data, dict) or isinstance(data, list)):
        return [(indent * level) + prefix + str(data) + "\n"]

    md_lines = []
    for header in data:
        md_lines.append((indent * level) + ("#" * (level + 1)) + " " + header + "\n")

        value = data[header]

        if isinstance(value, dict):

            md_lines.extend(toml_parse(value, level=level + 1))

        elif isinstance(value, list):
            pass

        else:
            md_lines.extend((indent * level) + prefix + str(value) + "\n")

    return md_lines


md_text_lines = toml_parse(toml_data)
print(json.dumps(md_text_lines, indent=4))

with open(OUT_FILE, "w") as outfile:
    outfile.writelines([ m +  "\n"  for m in md_text_lines])
