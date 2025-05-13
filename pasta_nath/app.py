import streamlit as st
import base64
from jinja2 import Template
import pdfkit
from PyPDF2 import PdfReader, PdfWriter
import io
import os

# Função para renderizar PDF a partir dos dados
def render_pdf(data):
    svg_dir = r"C:\Users\gonca\OneDrive\Área de Trabalho\IZE\Relatório Mensal\code\v2_relatorio_mensal\pasta_nath"
    # logo
    logo_path = os.path.join(svg_dir, "IZE-LOGO-2.svg")
    with open(logo_path, "r", encoding="utf-8") as f:
        logo_svg = f.read()
    # seta up verde
    seta_path = os.path.join(svg_dir, "SETA-UP-VERDE.svg")
    with open(seta_path, "rb") as f:
        seta_b64 = base64.b64encode(f.read()).decode("utf-8")
    # seta down laranja
    seta2_path = os.path.join(svg_dir, "SETA-DOWN-LARANJA.svg")
    with open(seta2_path, "rb") as f:
        seta_b64_2 = base64.b64encode(f.read()).decode("utf-8")
    # seta up laranja
    seta3_path = os.path.join(svg_dir, "SETA-UP-LARANJA.svg")
    with open(seta3_path, "rb") as f:
        seta_b64_3 = base64.b64encode(f.read()).decode("utf-8")
    # seta down verde
    seta4_path = os.path.join(svg_dir, "SETA-DOWN-VERDE.svg")
    with open(seta4_path, "rb") as f:
        seta_b64_4 = base64.b64encode(f.read()).decode("utf-8")

    # Template HTML usando Jinja2
    template_str = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Financeiro</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; padding:20px; }
        .section-title { font-size:25px; font-weight:bold; margin-top:6px; margin-bottom:40px}
        .notes-title {
            font-size: 18px;
            font-weight: 600;    /* deixa em negrito */
            margin: 35px 0 1px 0; /* seu espaçamento */
            text-align: left;
        }
        .notes-title + .box-frame {
            margin-top: 15px;
        }
        .bar-container {
            /* ocupa 100% da largura e esconde tudo que vaza */
            width: 100%;
            height: 30px;
            border-radius: 8px;
            overflow: hidden;
            margin: 2px 0 0 0;
        }
        .bar-segment {
            /* flutua para a esquerda, com altura de 100%,
                a largura já vem inline style via Jinja */
            float: left;
            height: 100%;
        }
        .bar-total { font-size:17px; text-align:right; margin-top:6px; }
        .value { font-size:25px; margin-top:-30px; margin-bottom:40px; font-weight:580; }
        hr.section-separator { border: none; border-top: 1px solid #ddd; margin:25px 0; }
        /* cor do nome do relatório */
        .report-name {
            color: #A5A5A5; 
        }
        /* cor do período */
        .report-period {
            color: #A5A5A5; 
        }
        table.cat-table { width:100%; border-collapse: collapse; margin-bottom:30px; border: none; }
        table.cat-table th, table.cat-table td {
            border: none;
            padding: 8px;
            text-align: left;
            background-color: #fff;
            font-family: 'Inter', sans-serif;
            font-weight: 200;
            font-size: 17px;
        }
        table.cat-table td:nth-child(3) { font-weight: 700; }
        table.cat-table td:nth-child(4) { font-size: 14px; }
        table.cat-table td:nth-child(5) { font-size: 14px; }
        table.cat-table thead { display: table-header-group; }
        table.cat-table thead th {
            visibility: hidden;
        }
        table.cat-table thead th:nth-child(4),
        table.cat-table thead th:nth-child(5) {
            visibility: visible;
            text-align: left;
            font-size: 14px;
            font-weight: 600;
        }
        .legend-box { width:12px; height:12px; border-radius:2px; }
        .var-up img {
            vertical-align: middle;
            width: 10px;
            height: 7px;
            margin-right: 3px;
        }
        .var-down img {
            vertical-align: middle;
            width: 10px;
            height: 7px;
            margin-right: 3px;
        }
        body {
            font-family: 'Inter', sans-serif;
            /* cria espaço no final para o footer não sobrepor conteúdo */
            padding: 20px 20px 80px 20px;  
            position: relative;
        }
        footer {
            position: fixed;
            bottom: -60px;
            left: 0;
            width: 100%;
            text-align: center;
            padding: 10px 0;
            background: transparent;
        }
        footer img {
            height: 40px;     
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
        /* contêiner com borda cinza arredondada */
        .box-frame {
            border: 1px solid #D9D9D9;
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 24px;
            margin-top: 50px;
        }
        /* quadrado em branco (vazio) */
        .box-frame.blank {
            height: 100px;       /* ajuste a altura conforme quiser */
            margin: 0 0 24px 0;  /* distância abaixo do bloco */
        }
        .notes-content {
            white-space: pre-wrap;   /* preserva quebras de linha */
            text-align: left;        /* garante que todo o texto fique alinhado à esquerda */
            margin: 0;               /* zera qualquer margem interna */
            padding: 0;              /* zera qualquer padding interno se houver */
            font-size: 17px;
            line-height: 1.6;
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
  <div class="box-frame">
    <div class="section">
      <div class="section-title">Receitas</div>
        {% set rec_colors = ['#007F4F','#33B283','#7FCEB1'] %}
        <div class="bar-container">
        {% for cat in data.receita_categories %}
            <div class="bar-segment"
                style="width: {{ cat.barra_rep }}%; background-color: {{ rec_colors[loop.index0] }};">
            </div>
        {% endfor %}
        </div>
        <div class="bar-total">
          {{ '%.0f'|format(data.represent_receita) }}%
        </div>
        <div class="value">R$ {{ '{:,.2f}'.format(data.receita).replace(',', 'X').replace('.', ',').replace('X', '.') }}</div>
        <table class="cat-table">
            <colgroup>
                <col style="width:5%" />
                <col style="width:35%" />
                <col style="width:30%" />
                <col style="width:15%" />
                <col style="width:15%" />
            </colgroup>
            <thead>
                <tr>
                <th></th>
                <th>Categoria</th>
                <th>Valor</th>
                <th>AV</th>
                <th>AH</th>
                </tr>
            </thead>
            <tbody>
            {% for cat in data.receita_categories %}
            <tr>
                <td><div class="legend-box" style="background-color:{{ rec_colors[loop.index0 % rec_colors|length] }};"></div></td>
                <td>{{ cat.name }}</td>
                <td>R$ {{ '{:,.2f}'.format(cat.value).replace(',', 'X').replace('.', ',').replace('X', '.') }}</td>
                <td>{{ '%.0f'|format(cat.representatividade) }}%</td>
                <td>
                    {% if cat.variacao >= 0 %}
                        <span class="var-up"> 
                        <img src="data:image/svg+xml;base64,{{ seta_b64 }}" alt="↑"/>
                        {{ '{:.1f}'.format(cat.variacao).replace('.', ',') }}%
                        </span>
                    {% else %}
                        <span class="var-down">
                        <img src="data:image/svg+xml;base64,{{ seta_b64_2 }}" alt="↑"/>
                        {{ '{:.1f}'.format(cat.variacao).replace('.', ',') }}%
                        </span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
            </tbody>
        </table>
    </div>
    <hr class="section-separator"/>
    <div class="section">
      <div class="section-title">Custos Variáveis</div>
        {% set cost_colors = ['#E75F00','#FF8733','#FFB37F'] %}
        <div class="bar-container">
        {% for cat in data.custo_categories %}
            <div class="bar-segment"
                style="width: {{ cat.barra_rep }}%; background-color: {{ cost_colors[loop.index0] }};">
            </div>
        {% endfor %}
        </div>
        <div class="bar-total">
          {{ '%.0f'|format(data.represent_custos) }}%
        </div>
        <div class="value">R$ {{ '{:,.2f}'.format(data.custos).replace(',', 'X').replace('.', ',').replace('X', '.') }}</div>
        <table class="cat-table">
            <colgroup>
                <col style="width:5%" />
                <col style="width:35%" />
                <col style="width:30%" />
                <col style="width:15%" />
                <col style="width:15%" />
            </colgroup>
            <thead>
                <tr>
                <th></th>
                <th>Categoria</th>
                <th>Valor</th>
                <th>AV</th>
                <th>AH</th>
                </tr>
            </thead>
            <tbody>
            {% for cat in data.custo_categories %}
            <tr>
                <td><div class="legend-box" style="background-color:{{ cost_colors[loop.index0 % cost_colors|length] }};"></div></td>
                <td>{{ cat.name }}</td>
                <td>R$ {{ '{:,.2f}'.format(cat.value).replace(',', 'X').replace('.', ',').replace('X', '.') }}</td>
                <td>{{ '%.0f'|format(cat.representatividade) }}%</td>
                <td>
                    {% if cat.variacao >= 0 %}
                        <span class="var-up"> 
                        <img src="data:image/svg+xml;base64,{{ seta_b64_3 }}" alt="↑"/>
                        {{ '{:.1f}'.format(cat.variacao).replace('.', ',') }}%
                        </span>
                    {% else %}
                        <span class="var-down">
                        <img src="data:image/svg+xml;base64,{{ seta_b64_4 }}" alt="↑"/>
                        {{ '{:.1f}'.format(cat.variacao).replace('.', ',') }}%
                        </span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
            </tbody>
        </table>
    </div>
  </div>
  <div class="notes-title">Notas</div>
  <div class="box-frame">
    <div class="notes-content">{{ data.notas }}</div>
    </div>
  </div>
  <footer>
    {{ logo_svg | safe }}
  </footer>
</body>
</html>
'''
    template = Template(template_str)
    html = template.render(
        data=data,
        logo_svg=logo_svg,
        seta_b64=seta_b64,
        seta_b64_2=seta_b64_2,
        seta_b64_3=seta_b64_3,
        seta_b64_4=seta_b64_4
    )
    path_wkhtml = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtml)
    relatório_bytes = pdfkit.from_string(
        html,
        False,
        options={"enable-local-file-access": None},
        configuration=config   
    )
        
    # lê a capa em memória e cria um BytesIO
    with open("marca/capa.pdf", "rb") as f:
        capa_bytes = f.read()
    capa_reader = PdfReader(io.BytesIO(capa_bytes))

    # abre o PDF gerado em memória
    relatório_reader = PdfReader(io.BytesIO(relatório_bytes))

    # faz o merge
    writer = PdfWriter()
    for page in capa_reader.pages:
        writer.add_page(page)
    for page in relatório_reader.pages:
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()

# Função principal do Streamlit
def main():
    st.title("Gerador do PDF do Relatório Mensal IZE")

    # Nome e Período
    nome = st.text_input("Nome", help="Digite aqui o nome do relatório")

    # Data
    periodo = st.text_input("Período", help="Digite aqui o período")

    # Notas
    notas = st.text_area("Notas", "", help="Digite notas do relatório (quebras de linha preservadas)")

    # Receita geral e representatividade
    receita = st.number_input("Receita (R$)", min_value=0.0, format="%.2f")
    represent_receita = st.number_input(
        "Representatividade Receita (%)", min_value=0.0, max_value=100.0, format="%.2f"
    )

    # Três blocos fixos de categorias de receita
    st.header("Categorias de Receita")
    receita_categories = []
    for i in range(3):
        st.subheader(f"Categoria Receita {i+1}")
        name = st.text_input(f"Nome Categoria Receita {i+1}", key=f"rec_name_{i}")
        value = st.number_input(f"Valor (R$) Categoria Receita {i+1}",
                                min_value=0.0, format="%.2f", key=f"rec_val_{i}")
        represent = st.number_input(f"Representatividade (%) Categoria Receita {i+1}",
                                    min_value=0.0, max_value=100.0, format="%.2f", key=f"rec_rep_{i}")
        variacao = st.number_input(f"Variação (%) Categoria Receita {i+1}",
                                   format="%.2f", key=f"rec_var_{i}")
        barra_rep = st.number_input(
            f"Representatividade da Barra Categoria Receita {i+1} (%)",
            min_value=0.0, max_value=100.0, format="%.2f",
            key=f"rec_barrep_{i}"
        )
        receita_categories.append({
            "name": name,
            "value": value,
            "representatividade": represent,
            "variacao": variacao,
            "barra_rep": barra_rep
        })

    # Custos gerais e representatividade
    custos = st.number_input("Custos Variáveis (R$)", min_value=0.0, format="%.2f")
    represent_custos = st.number_input(
        "Representatividade Custos Variáveis (%)", min_value=0.0, max_value=100.0, format="%.2f"
    )

    # Três blocos fixos de categorias de custo
    st.header("Categorias de Custo")
    custo_categories = []
    for i in range(3):
        st.subheader(f"Categoria Custo {i+1}")
        name = st.text_input(f"Nome Categoria Custo {i+1}", key=f"cost_name_{i}")
        value = st.number_input(f"Valor (R$) Categoria Custo {i+1}",
                                min_value=0.0, format="%.2f", key=f"cost_val_{i}")
        represent = st.number_input(f"Representatividade (%) Categoria Custo {i+1}",
                                    min_value=0.0, max_value=100.0, format="%.2f", key=f"cost_rep_{i}")
        variacao = st.number_input(f"Variação (%) Categoria Custo {i+1}",
                                   format="%.2f", key=f"cost_var_{i}")
        barra_rep = st.number_input(
            f"Representatividade da Barra Categoria Custo {i+1} (%)",
            min_value=0.0, max_value=100.0, format="%.2f",
            key=f"cost_barrep_{i}"
        )
        custo_categories.append({
            "name": name,
            "value": value,
            "representatividade": represent,
            "variacao": variacao,
            "barra_rep": barra_rep
        })

    # Gerar e baixar PDF
    if st.button("Gerar PDF"):
        data = {
            "nome": nome,
            "Periodo": periodo,
            "notas": notas, 
            "receita": receita,
            "represent_receita": represent_receita,
            "receita_categories": receita_categories,
            "custos": custos,
            "represent_custos": represent_custos,
            "custo_categories": custo_categories
        }
        pdf = render_pdf(data)
        st.download_button("Baixar Relatório PDF",
                           data=pdf,
                           file_name="relatorio.pdf",
                           mime="application/pdf")

if __name__ == "__main__":
    main()
