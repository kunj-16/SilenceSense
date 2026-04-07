from jinja2 import Template
from pathlib import Path

def generate_report(data, output_path):
    template_text = Path(
        "app/reports/templates/report.txt"
    ).read_text()

    template = Template(template_text)
    content = template.render(**data)

    with open(output_path, "w") as f:
        f.write(content)
