import os
from jinja2 import Template
import pdfkit

# Caminho para o executável wkhtmltopdf (ajuste conforme seu ambiente)
WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

def main():
    # Pergunta Nome e Período ao usuário
    nome = input("Digite o Nome do relatório: ")
    periodo = input("Digite o Período: ")

    # Lê o SVG da logo
    svg_path = os.path.join("marca", "IZE-LOGO-2.svg")
    with open(svg_path, "r", encoding="utf-8") as f:
        logo_svg = f.read()

    # Template HTML minimalista: header, período, bloco vazio e footer
    html_template = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório Mensal</title>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; margin:0; padding:0; }
        /* cor do nome do relatório */
        .report-name {
            color: #A5A5A5; 
        }
        /* cor do período */
        .report-period {
            color: #A5A5A5; 
        }
        /* barra laranja acima do cabeçalho */
            .header-accent {
            width: 100px;               /* ajuste a largura que quiser */
            height: 6px;               /* ajuste a espessura */
            background-color: #FF6900; /* laranja */
            margin: 0 0 4px 40px;
            border-radius: 3px 3px 0 0;        /* cantos levemente arredondados */
        }
        /* cabeçalho acima da primeira caixa */
            .report-header {
            border-top: 1px solid #D9D9D9;
            margin: 0 0 8px 0;
        }
        /* container com nome e período */
        .report-header-info {
            display: flex;
            justify-content: flex-start;   /* todos os itens começam à esquerda */
            align-items: center;
            width: 100%;
            font-size: 14px;
            margin: 4px 0 16px;
            white-space: nowrap;
        }
        /* empurra o segundo span para a margem direita */
        .report-header-info .report-period {
            margin-left: auto;
        }
        </style>
    </head>
    <body>
    <!-- barra laranja acima da linha -->
    <div class="header-accent"></div>
    <div class="report-header"></div>
    <table style="width:100%; border-collapse:collapse; margin:4px 0 16px;">
        <tr>
            <td class="report-name" style="padding:0; text-align:left;  font-size:14px;">
                {{ data.nome }}
            </td>
            <td class="report-period" style="padding:0; text-align:right; font-size:14px;">
                {{ data.Periodo }}
            </td>
        </tr>
    </table>
    </body>
    </html>
    """

    # Renderiza HTML
    template = Template(html_template)
    html = template.render(nome=nome, periodo=periodo, logo_svg=logo_svg)

    # Configurações do PDF
    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    options = {
        "enable-local-file-access": None,
        "margin-top": "10mm",
        "margin-bottom": "20mm",
        "margin-left": "10mm",
        "margin-right": "10mm",
    }

    # Gera o PDF
    output_file = "relatorio_em_branco.pdf"
    pdfkit.from_string(html, output_file, options=options, configuration=config)
    print(f"PDF gerado: {output_file}")

if __name__ == "__main__":
    main()