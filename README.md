# Benchmark_App_Python
Projeto para exibição de dados de benchmark de API's gerados pelo Postman Runner e geração de relatórios em PDF com Python.

### Requisitos:

Realizar a instalação da biblioteca *pdfkit*.

```bash
    pip install pdfkit
```

Além da necessidade da instalação das bibliotecas que estão dentro do requirements.txt, é necessário realizar o download de um executável chamado *wkhtmltopdf*.
Este executável é responsável pela conversão do template HTML para PDF.

[Download wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)

Também talvez será necessário alterar o caminho de onde foi instalado o wkhtmltopdf no arquivo *utils/report.py*, exemplo:

```py
    wkhtml_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
```

**OBS:**

Também há uma implementação de geração de relatório com a biblioteca *weasyprint*, porém precisará de baixar o seguinte runtime:

[GTK for Windows Runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)

E realizar as seguintes instalações de bibliotecas python:

```bash
    pip install weasyprint
    pip install cairocffi
```

#### Atenção:

O *pdfkit* utiliza como dependência o executável *wkhtmltopdf*. Infelizmente é baseado em uma versão antiga do Webkit e não possui suporte para muitos recursos modernos de CSS e Js, como por exemplo, o **flexbox**.

Caso seja necessário, você pode procurar por outras alternativas ao *wkhtmltopdf*, como por exemplo, o *weasyprint*.

Fonte: [Python HTML to PDF Libs](https://docraptor.com/python-html-to-pdf)