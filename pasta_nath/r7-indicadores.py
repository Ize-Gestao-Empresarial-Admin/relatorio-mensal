import streamlit as st
import base64
from jinja2 import Template
import pdfkit
from PyPDF2 import PdfReader, PdfWriter
import io
import os

# Função para renderizar PDF a partir dos dados
def render_pdf(data, indicadores):
    svg_dir = r"C:\Users\natha\OneDrive\Documentos\Relatório Mensal\marca"

    icon_path = os.path.join(svg_dir, "rodape.png")
    with open(icon_path, "rb") as f:
        icon_bytes = f.read()
    icon_rodape = base64.b64encode(icon_bytes).decode("ascii")

    icon_path = os.path.join(svg_dir, "LOGO-DINHEIRO-LARANJA.png")
    with open(icon_path, "rb") as f:
        icon_bytes = f.read()
    icon_din_lar = base64.b64encode(icon_bytes).decode("ascii")

    icon_path = os.path.join(svg_dir, "LOGO-DINHEIRO-VERDE.png")
    with open(icon_path, "rb") as f:
        icon_bytes = f.read()
    icon_din_ver = base64.b64encode(icon_bytes).decode("ascii")

    icon_path = os.path.join(svg_dir, "LOGO-PERCENTUAL-LARANJA.png")
    with open(icon_path, "rb") as f:
        icon_bytes = f.read()
    icon_per_lar = base64.b64encode(icon_bytes).decode("ascii")

    icon_path = os.path.join(svg_dir, "LOGO-PERCENTUAL-VERDE.png")
    with open(icon_path, "rb") as f:
        icon_bytes = f.read()
    icon_per_ver = base64.b64encode(icon_bytes).decode("ascii")

    icon_path = os.path.join(svg_dir, "LOGO-SU-LARANJA.png")
    with open(icon_path, "rb") as f:
        icon_bytes = f.read()
    icon_su_lar = base64.b64encode(icon_bytes).decode("ascii")

    icon_path = os.path.join(svg_dir, "LOGO-SU-VERDE.png")
    with open(icon_path, "rb") as f:
        icon_bytes = f.read()
    icon_su_ver = base64.b64encode(icon_bytes).decode("ascii")

    for ind in indicadores:
        # formatação R$
        if ind["unidade"] == "R$":
            ind["bom_fmt"]  = f"R$ {ind['bom']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ind["ruim_fmt"] = f"R$ {ind['ruim']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        # formatação %
        elif ind["unidade"] == "%":
            ind["bom_fmt"]  = f"{ind['bom'] * 100:.2f}%"
            ind["ruim_fmt"] = f"{ind['ruim'] * 100:.2f}%"
        # sem formatação extra
        else:
            ind["bom_fmt"]  = str(ind["bom"])
            ind["ruim_fmt"] = str(ind["ruim"])

    # Template HTML usando Jinja2
    template_str = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Mensal</title>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;400;600;700&family=Poppins:wght@400;600;700&display=swap');
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

    .cards-container {
    margin-top: 16px;    /* espaçamento acima dos cards */
    }
    .cards-container .indicator-card:nth-child(-n+3) {
    margin-top: 67px;    /* só use se quiser pular a primeira fileira */
    }
    .cards-container::after {
    content: "";
    display: table;
    clear: both;
    }

    .indicator-card {
    position: relative;
    float: left;
    margin-right: 30px;
    margin-bottom: 50px;
    width: 245px;
    height: 112px;
    border: 1px solid #CFCFCF;
    border-radius: 9px;
    box-sizing: border-box;
    overflow: hidden;
    }

    /* faixa verde no topo */
    .indicator-card .card-header {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 7px;
    background-color: #009F64;
    border-top-left-radius: 9px;
    border-top-right-radius: 9px;
    }

    /* círculo com o ícone, sempre fixo */
    .indicator-card .icon-circle {
    position: absolute;
    top: 30px;    /* afasta do topo do card */
    left: 16px;   /* afasta da borda esquerda */
    width: 48px;
    height: 48px;
    background-color: #FFFFFF;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    }

    /* bloco de texto (nome + valor) sempre alinhado ao mesmo top */
    .indicator-card .text-block {
    position: absolute;
    top: 27px;     /* mesmo deslocamento vertical do ícone */
    left: 80px;    /* 16px padding + 48px ícone + 16px gap */
    right: 16px;   /* padding direito */
    }

    /* nome do indicador */
    .indicator-card .indicator-name {
    font-size: 16px;
    font-weight: 200;
    line-height: 1;
    margin: 0 0 4px 0;
    font-family: 'Inter', sans-serif;
    }

    /* valor principal */
    .indicator-card .indicator-value {
    font-size: 17px;
    font-weight: 700;
    font-family: 'Poppins', sans-serif;
    margin: 0;
    }

    /* Frase colado na base direita */
    .scenario-text {
    position: absolute;
    bottom: 5px;
    right: 7px;
    font-size: 8px;
    color: #878787;
    margin: 0;
    text-align: right;
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

<div class="cards-container">
  {% for ind in indicadores %}
  <div class="indicator-card">
    <div class="card-header"></div>

    <!-- ícone fixo -->
    <div class="icon-circle">
      <img src="data:image/png;base64,{{ icon_din_ver }}" width="48" alt="ícone">
    </div>

    <!-- texto (nome + valor) sempre posicionado a partir do mesmo top -->
    <div class="text-block"
     style="top: {{ 
        '17px' if ind.nome|length > 60 else 
        '20px' if ind.nome|length > 40 else 
        '27px' 
        }};">
      <div class="indicator-name"
        style="font-size:{{ 
        '12px'  if ind.nome|length > 60 else 
        '13px' if ind.nome|length > 40 else 
        '16px' 
        }};">
    {{ ind.nome }}
    </div>

    <div class="indicator-value"
        style="font-size:{{ '15px' if ind.valor >= 999999999 else '18px' }};">
    {% if ind.unidade == '%' %}
        {% set valor_para_formatar = ind.valor * 100 %}
    {% else %}
        {% set valor_para_formatar = ind.valor %}
    {% endif %}
            
    {{ ind.unidade }}
    {{ "{:,.2f}".format(valor_para_formatar)
        | replace(',', 'X')
        | replace('.', ',')
        | replace('X', '.') }}
      </div>
    </div>

        <div
          class="scenario-text"
          style="font-size:{{ '7px' if ind.bom >= 10000000 else '8px' }};"
        >
          O cenário bom é {{ ind.bom_fmt }}  
          e o ruim é {{ ind.ruim_fmt }}
        </div>
      </div>
    </div>
  {% endfor %}

</div>
</body>
</html>
'''
    template = Template(template_str)
    html = template.render(
        data=data,
        indicadores=indicadores,
        icon_rodape=icon_rodape,
        icon_din_lar=icon_din_lar,
        icon_din_ver=icon_din_ver,
        icon_per_lar=icon_per_lar,
        icon_per_ver=icon_per_ver,
        icon_su_lar=icon_su_lar,
        icon_su_ver=icon_su_ver,
    )
    path_wkhtml = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtml)
    relatório_bytes = pdfkit.from_string(
        html,
        False,
        options={
            "enable-local-file-access": None,
            "margin-top":    "14mm",
            "margin-bottom": "5mm", 
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
    
    # 1) Campos fixos
    nome = st.text_input("Nome", help="Digite aqui o nome do relatório")
    periodo = st.text_input("Período", help="Digite aqui o período")
    
    # 2) Inicializa sessão para indicadores
    if "indicadores" not in st.session_state:
        st.session_state.indicadores = []

    # 3) Botão para adicionar novo bloco
    if st.button("➕ Adicionar indicador"):
        st.session_state.indicadores.append({
            "nome": "",
            "valor": 0.0,
            "cenario": 0,
            "bom": 0.0,
            "ruim": 0.0,
            "unidade": "R$"
        })

    # 4) Renderiza um bloco de inputs para cada indicador
    for i, ind in enumerate(st.session_state.indicadores):
        exp = st.expander(f"Indicador #{i+1}", expanded=True)
        with exp:
            cols = st.columns([2,1,1,1,1,1,0.5])
            ind["nome"] = cols[0].text_input("Nome indicador", value=ind["nome"], key=f"nome_{i}")
            ind["valor"] = cols[1].number_input("Valor indicador", value=ind["valor"], key=f"valor_{i}")
            ind["cenario"] = cols[2].selectbox("Cenário", options=[1,0,-1], index=[1,0,-1].index(ind["cenario"]), key=f"cenario_{i}")
            ind["bom"]    = cols[3].number_input("Bom", value=ind["bom"], key=f"bom_{i}")
            ind["ruim"]   = cols[4].number_input("Ruim", value=ind["ruim"], key=f"ruim_{i}")
            ind["unidade"]= cols[5].selectbox("Unidade", options=["R$", "%", "SU"], index=["R$", "%", "SU"].index(ind["unidade"]), key=f"unidade_{i}")
            # botão para remover este indicador
            if cols[6].button("❌", key=f"del_{i}"):
                st.session_state.indicadores.pop(i)
                st.experimental_rerun()

    st.markdown("---")
    # 5) Botão de gerar PDF, agora passando a lista de indicadores
    if st.button("🖨️ Gerar PDF"):
        data = {
            "nome": nome,
            "Periodo": periodo,
        }
        indicadores = st.session_state.indicadores
        pdf_bytes = render_pdf(data, indicadores)
        st.download_button(
            "Baixar Relatório PDF",
            data=pdf_bytes,
            file_name="relatorio.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
