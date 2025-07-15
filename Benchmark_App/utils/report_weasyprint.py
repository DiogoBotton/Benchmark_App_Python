from weasyprint import HTML
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import tempfile

def generate_pdf(benchmark_data, df_comparativo):
    # Carrega o template
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("template.html")

    # Renderiza o HTML
    html_content = template.render(
        benchmarks=benchmark_data,
        comparativo=df_comparativo
    )

    # Cria arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        HTML(string=html_content).write_pdf(tmp_file.name)
        return tmp_file.name
