import pdfkit
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import tempfile

def generate_pdf(benchmark_data, df_comparativo):
    # Caminho do executável responsável pela conversão de HTML para PDF
    wkhtml_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

    # Verifica se o path existe
    if not os.path.exists(wkhtml_path):
        raise FileNotFoundError(f"wkhtmltopdf não encontrado em: {wkhtml_path}")

    # Cria configuração
    config = pdfkit.configuration(wkhtmltopdf=wkhtml_path)

    # Adquire o template
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("template.html")

    # Renderiza o HTML
    html = template.render(
        benchmarks=benchmark_data,
        comparativo=df_comparativo,
        tempoReferencia="Tempo médio"
    )

    # Gera PDF temporário
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_file.close()

    pdfkit.from_string(html, tmp_file.name, configuration=config)

    # Retorna o caminho do arquivo temporário
    return tmp_file.name
