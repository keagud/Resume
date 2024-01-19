import datetime as dt
from jinja2 import FileSystemLoader, Environment
from pathlib import Path

from pdfkit import from_file

def html_to_pdf(input_file: Path, output_pdf: Path):
    from_file(str(input_file), str(output_pdf))

def insert_css(input_html: Path, output_html: Path, css_file: Path):
    loader = FileSystemLoader(input_html.parent)
    env = Environment(loader=loader)
    template = env.get_template(input_html.name)

    with open(css_file, "r") as fp:
        css_content = fp.read()

    output_content = template.render({"styles": css_content})

    with open(output_html, "w") as fp:
        fp.write(output_content)


def main():
    print(f"RUNNING {dt.datetime.now().isoformat()}")

    kwargs = dict(
        input_html=Path("./input.html"),
        output_html=Path("./output_pdf.html"),
        css_file=Path("./pdf.css"),
    )

    insert_css(**kwargs)

    html_to_pdf(Path("./output_pdf.html"), Path("./f.pdf"))




if __name__ == "__main__":
    main()
