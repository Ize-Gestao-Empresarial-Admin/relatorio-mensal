import streamlit as st
import base64
from jinja2 import Template
import pdfkit
from PyPDF2 import PdfReader, PdfWriter
import io
import os

# Função para renderizar PDF a partir dos dados
def render_pdf(data):
    svg_dir = r"C:\Users\gonca\OneDrive\Área de Trabalho\IZE\Relatório Mensal\code\v2_relatorio_mensal\assets\icons"
    # logo
    logo_path = os.path.join(svg_dir, "IZE-LOGO-1.svg")
    with open(logo_path, "r", encoding="utf-8") as f:
        logo_svg = f.read()

    # Template HTML usando Jinja2
    template_str = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório em Branco</title>
    <style>
    /* importa Inter, Poppins e Ruda */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Poppins:wght@400;600;700&family=Ruda:wght@400;500;600;700&display=swap');
    body { font-family: 'Inter', sans-serif; }

    /* cor do nome do relatório */
    .report-name { color: #A5A5A5; }
    /* cor do período */
    .report-period { color: #A5A5A5; }
    /* barra laranja acima do cabeçalho */
    .header-accent {
        width: 100px;
        height: 6px;
        background-color: #FF6900;
        margin: 0 0 4px 40px;
        border-radius: 3px 3px 0 0;
    }
    /* linha abaixo da barra */
    .report-header {
        border-top: 1px solid #D9D9D9;
        margin: 0 0 8px 0;
    }
    /* container do nome e período */
    .report-header-info {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        width: 100%;
        font-size: 14px;
        margin: 60px 0 16px;
        white-space: nowrap;
    }
    .report-header-info .report-period {
        margin-left: auto;
    }
    
    /* NOVO: título da seção abaixo do cabeçalho */
    /* 2) título principal grande em Poppins */
    .section-title {
        font-family: 'Poppins', sans-serif;
        font-size: 44px;
        font-weight: 700;
        color: #404040;
        margin: 40px 0 5px;
        padding-left: 87mm;  /* 16mm = mesma margem que left/right do seu pdfkit */
    }
    /* 3) container dos itens numerados */
    .section-list {
        padding-left: 87mm; 
        margin-bottom: 30px;
    }
    .section-item {
        display: table;
        width: 100%;
        margin-bottom: 16px;
    }
    .item-number {
        display: table-cell;
        vertical-align: top;
        width: 53px;              /* ajusta conforme quiser de espaço pro número */
        font-family: 'Ruda', sans-serif;
        font-size: 25px;
        font-weight: 100;
        color: #A6A6A6;
        padding-right: -10px;      /* distância até o texto */
    }
    .item-texts {
        display: table-cell;
        vertical-align: top;
    }

    .item-title {
        font-family: 'Ruda', sans-serif;
        font-size: 18px;
        font-weight: 100;
        color: #7F7F7F;
        margin-bottom: -1px;
        margin-top: 5px;
    }

    .item-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        font-weight: 400;
        color: #7F7F7F;
        margin-top: -3px;
    }

    .page-content {
      display: flex;
      align-items: flex-start;
      /* se quiser ajustar o topo, mude esse margin-top */
      margin-top: 10mm;
    }

    .logo-side {
      flex: 0 0 30mm;    /* reserva 30 mm de largura para o logo */
      padding-right: 5mm;/* espaço entre o logo e o conteúdo */
    }

    .logo-side svg {
      width: 100%;
      height: auto;
    }

    .main-sections {
      flex: 1;           /* ocupa o espaço restante */
    }   

    .header-wrapper {
      position: relative;
      margin-bottom: 16px;
    }
    .logo-bg {
      position: absolute;
      top: 2mm;
      left: 50%;
      transform: translateX(-50%);
      z-index: 0;       /* agora fica atrás do header, mas acima do fundo do body */
      opacity: 0.1;
    }
    .logo-bg svg {
      width: 30mm;
      height: auto;
    }

    .header-accent,
    .report-header,
    .report-header-info {
      position: relative;
      z-index: 1;      /* garante que estejam acima do SVG */
    }
    .header-accent {
      width: 100px; height: 6px;
      background: #FF6900;
      margin: 0 0 4px 40px;
      border-radius: 3px 3px 0 0;
    }
    .report-header {
      border-top: 1px solid #D9D9D9;
      margin: 0 0 8px 0;
    }
    .report-header-info {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 16mm;
      font-size: 14px;
      color: #A5A5A5;
      white-space: nowrap;
    }

    /* seção de índice / títulos numerados etc. */
    .section-title {
      font-family: 'Poppins', sans-serif;
      font-size: 44px; font-weight: 700;
      color: #404040;
      margin: 40px 0 5px;
      padding-left: 87mm;
    }
    .section-list {
      padding-left: 87mm;
      margin-bottom: 30px;
    }
    .section-item {
      display: table;
      width: 100%;
      margin-bottom: 16px;
    }
    .item-number {
      display: table-cell;
      vertical-align: top;
      width: 53px;
      font-family: 'Ruda', sans-serif;
      font-size: 25px; font-weight: 100;
      color: #A6A6A6;
    }
    .item-texts {
      display: table-cell;
      vertical-align: top;
    }
    .item-title {
      font-family: 'Ruda', sans-serif;
      font-size: 18px; font-weight: 100;
      color: #7F7F7F;
      margin-top: 5px; margin-bottom: 0;
    }
    .item-subtitle {
      font-family: 'Inter', sans-serif;
      font-size: 11px; font-weight: 400;
      color: #7F7F7F;
      margin-top: 2px;
    } 
    </style>
</head>
<body>

  <!-- 1) Wrapper relativo -->
  <div class="header-wrapper">
    <!-- este é o nosso fundo absoluto -->
    <div class="logo-bg">
      {{ logo_svg | safe }}
    </div>

  <div class="header-accent"></div>
  <div class="report-header"></div>
    <table style="width:100%; border-collapse:collapse; margin:4px 0 16px;">
      <tr>
          <td class="report-name" style="padding:0; text-align:left; font-size:14px;">
              {{ data.nome }}
          </td>
          <td class="report-period" style="padding:0; text-align:right; font-size:14px;">
              {{ data.Periodo }}
          </td>
      </tr>
    </table>
    </div>
  </div>

  {% if data.fluxo_caixa == 'Sim' %}
    <div class="section-title">Fluxo de Caixa</div>
    <div class="section-list">
      <div class="section-item">
        <span class="item-number">01</span>
        <div class="item-texts">
          <div class="item-title">Análise de Fluxo de Caixa – Parte 1</div>
          <div class="item-subtitle">Análise de receitas e custos variáveis</div>
        </div>
      </div>

      <div class="section-item">
        <span class="item-number">02</span>
        <div class="item-texts">
          <div class="item-title">Análise de Fluxo de Caixa - Parte 2</div>
          <div class="item-subtitle">Análise de lucro bruto e despesas fixas</div>
        </div>
      </div>
      
      <div class="section-item">
        <span class="item-number">03</span>
        <div class="item-texts">
          <div class="item-title">Análise de Fluxo de Caixa – Parte 3</div>
          <div class="item-subtitle">Análise de lucro operacional e investimentos</div>
        </div>
      </div>

      <div class="section-item">
        <span class="item-number">04</span>
        <div class="item-texts">
          <div class="item-title">Análise de Fluxo de Caixa – Parte 4</div>
          <div class="item-subtitle">Análise de lucro líquido e resultados não operacionais</div>
        </div>
      </div>

      <div class="section-item">
        <span class="item-number">05</span>
        <div class="item-texts">
          <div class="item-title">Análise de Fluxo de Caixa – Parte 5</div>
          <div class="item-subtitle">Análise de saídas não operacionais e geração de caixa</div>
        </div>
      </div>
    </div>
  {% endif %}

  {% if data.dre_gerencial == 'Sim' %}
    <div class="section-title">DRE Gerencial</div>
    <div class="section-list">
      <div class="section-item">
        <span class="item-number">06</span>
        <div class="item-texts">
          <div class="item-title">Demonstrativo do resultado de exercício</div>
          <div class="item-subtitle">Análise de competência</div>
        </div>
      </div>
    </div>
  {% endif %}

  {% if data.indicador == 'Sim' %}
    <div class="section-title">Indicadores</div>
    <div class="section-list">
      <div class="section-item">
        <span class="item-number">07</span>
        <div class="item-texts">
          <div class="item-title">Indicadores Gerais</div>
          <div class="item-subtitle">Análise dos indicadores gerais</div>
        </div>
      </div>
    </div>
  {% endif %}

  {% if data.nota_consultor == 'Sim' %}
    <div class="section-title">Nota do Consultor</div>
    <div class="section-list">
      <div class="section-item">
        <span class="item-number">08</span>
        <div class="item-texts">
          <div class="item-title">Parecer Técnico</div>
          <div class="item-subtitle">Nota manual do consultor</div>
        </div>
      </div>
    </div>
  {% endif %}

  {% if data.marca == 'Sim' %}
    <div class="section-title">Marca</div>
    <div class="section-list">
      <div class="section-item">
        <span class="item-number">09</span>
        <div class="item-texts">
          <div class="item-title">Redes Sociais</div>
          <div class="item-subtitle">Instagram, Linkedin e Blog</div>
        </div>
      </div>
      <div class="section-item">
        <span class="item-number">10</span>
        <div class="item-texts">
          <div class="item-title">Redes Sociais</div>
          <div class="item-subtitle">Youtube e ZNews</div>
        </div>
      </div>
    </div>
  {% endif %}

</body>
</html>
'''
    template = Template(template_str)
    html = template.render(
        data=data,
        logo_svg=logo_svg
    )
    path_wkhtml = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtml)
    relatório_bytes = pdfkit.from_string(
        html,
        False,
        options={
            "enable-local-file-access": None,
            "margin-top":    "14mm",
            "margin-bottom": "5mm",   # espaço para o footer (agora fixo)
            "margin-left":   "16mm",
            "margin-right":  "16mm",
        },
        configuration=config   
    )
        
    # abre o PDF gerado em memória
    relatório_reader = PdfReader(io.BytesIO(relatório_bytes))

    # faz o merge
    writer = PdfWriter()
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
    periodo = st.text_input("Período", help="Digite aqui o período")

    # Nova pergunta
    fluxo = st.radio("Fluxo de Caixa?", ["Sim", "Não"], index=0)
    dre = st.radio("DRE?", ["Sim", "Não"], index=0)
    indicador = st.radio("Indicador?", ["Sim", "Não"], index=0)
    nota = st.radio("Nota do consultor?", ["Sim", "Não"], index=0)
    marca = st.radio("Marca?", ["Sim"], index=0)

    # Gerar e baixar PDF
    if st.button("Gerar PDF"):
        data = {
            "nome": nome,
            "Periodo": periodo,
            "fluxo_caixa": fluxo,
            "dre_gerencial": dre,
            "indicador": indicador,
            "nota_consultor": nota,
            "marca": marca
        }
        pdf = render_pdf(data)
        st.download_button("Baixar Relatório PDF",
                           data=pdf,
                           file_name="relatorio.pdf",
                           mime="application/pdf")

if __name__ == "__main__":
    main()
