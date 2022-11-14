import toml, argparse, json

# parser = argparse.ArgumentParser()

# parser.add_argument('input')
# parser.add_argument('-o', '--output')
# args = parser.parse_args()

IN_FILE = "resume.toml"
OUT_FILE = "resume-toml.md"

with open(IN_FILE, "r") as infile:
    toml_data = toml.load(infile)

# print(json.dumps(toml_data, indent=4))


def toml_parse(data, level=0, indent=" ", list_item = False) -> list[str]:
    md_lines = []

    makeline = lambda c, p="": "".join(((indent * level), p, str(c)))
    primitive = lambda x: not (isinstance(x, list) or isinstance(x, dict))

    if isinstance(data, dict):
        for header in data:
            md_lines.append(('#' * (level + 1)) + " " + header + "\n" )
            md_lines.extend(toml_parse(data[header], level = level + 1, indent=indent))

    elif isinstance(data, list):
        for item in data:
            item_prefix = "-" if primitive(item) else ""

    else:
        pass



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
    outfile.writelines(md_text_lines)
