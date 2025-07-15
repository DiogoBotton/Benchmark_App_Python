# Benchmark_App_Python
Projeto para exibição de dados de benchmark de API's gerados pelo Postman Runner e geração de relatórios em PDF com Python.

### Requisitos:

Além da necessidade da instalação das bibliotecas que estão dentro do requirements.txt, é necessário realizar o download de um executável chamado *wkhtmltopdf*.
Este executável é responsável pela conversão do template HTML para PDF.

[Download wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)

Também talvez será necessário alterar o caminho de onde foi instalado o wkhtmltopdf no arquivo *utils/report.py*, exemplo:

```py
    wkhtml_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
```