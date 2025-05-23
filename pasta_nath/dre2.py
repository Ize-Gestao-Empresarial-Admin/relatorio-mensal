import streamlit as st
from jinja2 import Template
import pdfkit
from PyPDF2 import PdfReader, PdfWriter
import io
import matplotlib.pyplot as plt
import textwrap
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib.patches import Rectangle
import base64, re, os

def y_fmt(value, tick_number):
    abs_val = abs(value)
    if abs_val >= 1_000_000:
        return f"{value/1_000_000:.0f}M"
    elif abs_val >= 1_000:
        return f"{value/1_000:.0f}k"
    else:
        return f"{value:.0f}"

def make_waterfall_base64(dre_items):
    # 1) prepara labels, valores e acumulados
    labels = [d["label"] for d in dre_items]
    values = [d["value"] for d in dre_items]
    bottoms = [0]
    for v in values[:-1]:
        bottoms.append(bottoms[-1] + v)

    # 2) cria figura
    fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
    bar_width      = 0.6
    colors = ['#009F64' if v >= 0 else '#FF6900' for v in values]

    # 3) desenha as linhas pontilhadas de conexão
    cumul = [0]
    for v in values:
        cumul.append(cumul[-1] + v)
    for i in range(len(values)-1):
        y  = cumul[i+1]
        x1 = i + bar_width/2
        x2 = (i+1) - bar_width/2
        ax.hlines(y, x1, x2,
                  colors="#CCCCCC",
                  linestyles="--",
                  linewidth=1,
                  zorder=0)

    # 4) desenha a linha de zero
    ax.axhline(0, color="#E5E5E5", linewidth=1, zorder=0)

    # 5) desenha cada barra com cantos arredondados
    for i, (val, bot, col) in enumerate(zip(values, bottoms, colors)):
        if val >= 0:
            y, height = bot, val
        else:
            y, height = bot + val, -val
        x = i - bar_width/2

        # borda com joinstyle='round' e edgecolor=facecolor
        rect = Rectangle(
            (x, y),
            bar_width,
            height,
            facecolor=col,
            edgecolor=col,
            linewidth=5,
            joinstyle='round',
            zorder=1
        )
        ax.add_patch(rect)

    # 6) estiliza eixos
    ax.grid(False)
    for spine in ("top","right"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#69696F")
    ax.spines["left"].set_color("#69696F")
    ax.spines["bottom"].set_linewidth(0.5)
    ax.spines["left"].set_linewidth(0.5)

    # 7) ticks e labels
    wrapped = ["\n".join(textwrap.wrap(l, width=15)) for l in labels]
    ax.set_xticks(range(len(wrapped)))
    ax.set_xlim(-0.5, len(wrapped)-0.5)
    ax.set_xticklabels(wrapped, rotation=0, ha="center", fontsize=10)
    ax.tick_params(axis='both', which='major', length=0, labelcolor="#69696F", pad=12)
    ax.spines['bottom'].set_position(('outward', 10))
    ax.xaxis.set_ticks_position('bottom')
    ax.margins(y=0.05)

    # conecta a linha de zero à base do axes
    # 1) Descobre onde, em fração de 0–1, fica o x=0 (primeira barra)
    x0_data = 0  # posição da primeira barra em dados
    xlim = ax.get_xlim()  # normalmente (-0.5, len(labels)-0.5)
    x0_frac = (x0_data - xlim[0]) / (xlim[1] - xlim[0])
    # 2) Desenha, em coords de eixo, a “perna” que conecta y=0 a y=-0.02 (2% pra baixo)
    ax.vlines(
        x=x0_frac-0.1,          # fração no eixo X
        ymin=-0.046,         # 2% abaixo do fundo (axes coords)
        ymax=0,             # na altura y=0 do gráfico (axes coords)
        transform=ax.transAxes,  # ambos x e y em coords de eixos
        colors="#69696F",
        linewidth=0.5,
        clip_on=False
    )

    # 8) formata o eixo Y
    ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))
    ax.yaxis.set_major_locator(MaxNLocator(6))

    fig.subplots_adjust(bottom=0.25)
    plt.tight_layout()

    # 9) exporta base64
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=800)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# Função para renderizar PDF a partir dos dados
def render_pdf(data):
    # 1) monta a lista de itens do waterfall
    dre_items = [
      {"label": "Faturamento",               "value": data["Faturamento"]},
      {"label": "Deduções da receita bruta", "value": data["Deduções"]},
      {"label": "Custos Variáveis",          "value": data["Custos Variáveis"]},
      {"label": "Despesas Fixas",            "value": data["Despesas Fixas"]},
      {"label": "EBITDA",                    "value": data["EBITDA"]},
    ]

    # gera o gráfico em PNG Base64
    chart_base64 = make_waterfall_base64(dre_items)

    # >>> Coloque aqui os cálculos de totais <<<
    positive_total = sum(item["value"] for item in dre_items if item["value"] >= 0)
    negative_total = sum(abs(item["value"]) for item in dre_items if item["value"] < 0)
    range_total   = positive_total + negative_total

    # --- 2) leitura do SVG da marca 
    svg_dir = r"C:\Users\natha\OneDrive\Documentos\Relatório Mensal\marca"
    fat_path = os.path.join(svg_dir, "rodape.png")
    with open(fat_path, "rb") as f:
        icon_bytes = f.read()
    icon_rodape = base64.b64encode(icon_bytes).decode("ascii")

    # Leitura dos icones
    fat_path = os.path.join(svg_dir, "LOGO-FATURAMENTO.png")
    with open(fat_path, "rb") as f:
        icon_bytes = f.read()
    icon_png_b64 = base64.b64encode(icon_bytes).decode("ascii")

    cust_path = os.path.join(svg_dir, "LOGO-LUCRO-LARANJA.png")
    with open(cust_path, "rb") as f:
        icon_bytes = f.read()
    icon_png_b64_2 = base64.b64encode(icon_bytes).decode("ascii")

    cust_path = os.path.join(svg_dir, "LOGO-CMV.png")
    with open(cust_path, "rb") as f:
        icon_bytes = f.read()
    icon_png_b64_3 = base64.b64encode(icon_bytes).decode("ascii")

    cust_path = os.path.join(svg_dir, "LOGO-DESPESAS.png")
    with open(cust_path, "rb") as f:
        icon_bytes = f.read()
    icon_png_b64_4 = base64.b64encode(icon_bytes).decode("ascii")

    cust_path = os.path.join(svg_dir, "LOGO-LUCRO-VERDE.png")
    with open(cust_path, "rb") as f:
        icon_bytes = f.read()
    icon_png_b64_5 = base64.b64encode(icon_bytes).decode("ascii")

    # Template HTML usando Jinja2
    template_str = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Mensal</title>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    body { font-family: 'Inter', sans-serif; margin:0; padding:0; }
    .section-title { font-size:25px; font-weight:bold; margin-top:1px; margin-bottom:40px}
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
    /* contêiner com borda cinza arredondada */
    .box-frame {
        page-break-inside: avoid;
        border: 1px solid #D9D9D9;
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 18px;
        margin-top: 45px;
        position: relative;
    }
    /* quadrado em branco (vazio) */
    .box-frame.blank {
        height: 100px;       /* ajuste a altura conforme quiser */
        margin: 0 0 24px 0;  /* distância abaixo do bloco */
    }

    .metrics-row {
        display: flex;
        justify-content: flex-start;
        gap: 24px;
        margin-top: 60px;
        /* flex-wrap padrão só na segunda linha */
    }

    /* sobrescreve SÓ para a primeira linha */
        .metrics-row.no-wrap {
        flex-wrap: nowrap;  /* força TODOS numa só linha, sem quebra */
    }
       
    .metric-card {
        position: relative;    
        display: inline-block;
        border: 1.3px solid #CFCFCF;
        border-radius: 12px;
        padding: 16px 6px 12px;
        width: 190px;
        background: white;
        box-sizing: border-box;
        text-align: center;
        min-height: 110px;
        vertical-align: top;
    }

    .metrics-row .metric-card {
        margin-right: 20px;  
    }
    .metrics-row .metric-card:last-child {
        margin-right: 0;
    }

    /* só o título do primeiro card */
    .metrics-row .metric-card:first-child .metric-label {
        margin-top: 13px;   /* antes era 4px, agora dobra para 8px */
    }

    /* só o título do último card */
    .metrics-row .metric-card:last-child .metric-label {
        margin-top: 13px;
    }

    /* Segunda linha (.metrics-row), segundo card (Lucro Operacional) */
    .metric-card--operacional .metric-label {
        margin-top: 13px;  /* ajuste o valor que precisar */
    }

    .metrics-row + .metrics-row {
        margin-top: 60px;  /* aumente ou diminua esse valor como quiser */
        margin-left: 120px; /* ajuste pra quanto quiser deslocar */
        margin-right: 20px;
    }

    .metric-icon {
        position: absolute;
        top: -27px;
        left: 38%;
        transform: translateX(-50%);
        background-color: #FFFFFF;
        border-radius: 50%;
        width: 45px;          /* um pouco maior que o ícone */
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2;
    }

    .metric-icon img {
        width: 45px;
        height: 45px;
    }

    .metric-label {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        color: #333333;
        margin-bottom: 0.7px;
        margin-top: 4px;
    }

    .metric-value {
        font-family: 'Inter', sans-serif;
        font-size: 17px;
        font-weight: 500;
        margin-bottom: 2px;
    }

    .metric-percent {
        font-family: 'Inter', sans-serif;
        font-size: 10px;
        color: #69696F;
    }

    .notes-title {
        font-size: 18px;
        font-weight: 600;    /* deixa em negrito */
        margin: 15px 0 1px 0; /* seu espaçamento */
        text-align: left;
    }
    .notes-title + .box-frame {
        margin-top: 12px;      /* antes era 45px na .box-frame geral */
        margin-bottom: 8px;
        padding: 30px;
    }
    .notes-content {
        white-space: pre-wrap;   /* preserva quebras de linha */
        text-align: left;        /* garante que todo o texto fique alinhado à esquerda */
        margin: 0;               /* zera qualquer margem interna */
        padding: 0;              /* zera qualquer padding interno se houver */
        font-size: 17px;
        line-height: 1.7;
    }

    .fixed-footer-bg {
        position: fixed;           /* sai do fluxo normal */
        bottom: -130px;                 /* gruda na base da página */
        left: 45%;                 /* centraliza horizontalmente */
        transform: translateX(-50%);
        z-index: -1;               /* garante que fique atrás de tudo */
        width: 80px;              /* ajuste à largura que desejar */
        height: auto;
        /* opacity: 1;           — opcional, se quiser “esmaecer” um pouco */
    }
    </style>
</head>
<body>
<img
    src="data:image/png;base64,{{ icon_rodape }}"
    class="fixed-footer-bg"
    alt=""
/>

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

<div class="box-frame" style="position: relative;">
  <div class="section-title">DRE - Análise por Competência</div>
  <img src="data:image/png;base64,{{ chart_base64 }}"
       style="width:100%; height:auto; margin-top:1rem;"
       alt="Waterfall DRE"/>
</div>

  <!-- === cards de métricas lado a lado === -->
  <div class="metrics-row no-wrap">
    <!-- card 1 -->
    <div class="metric-card">
      <div class="metric-icon">
        <img src="data:image/png;base64,{{ icon_png_b64 }}"
             width="50" height="50" alt="Ícone Faturamento"/>
      </div>
      <div class="metric-label">Faturamento</div>
      <div class="metric-value">
        R$ {{ "{:,.2f}".format(data["Faturamento"]) }}
      </div>
      <div class="metric-percent">
        {{ data["Representatividade Faturamento (%)"] }}%
      </div>
    </div>

    <!-- card 2 -->
    <div class="metric-card">
      <div class="metric-icon">
        <img src="data:image/png;base64,{{ icon_png_b64_2 }}"
             width="50" height="50" alt="Ícone CV e Deduções"/>
      </div>
      <div class="metric-label">Custos variáveis + deduções da receita</div>
      <div class="metric-value">
        R$ {{ "{:,.2f}".format(data["Custos e Deduções"]) }}
      </div>
      <div class="metric-percent">
        {{ data["Representatividade Custos e Deduções (%)"] }}%
      </div>
    </div>

    <!-- card 3 -->
    <div class="metric-card">
      <div class="metric-icon">
        <img src="data:image/png;base64,{{ icon_png_b64_3 }}"
             width="45" height="45" alt="Ícone CMV"/>
      </div>
      <div class="metric-label">Custos com Produtos e Serviços</div>
      <div class="metric-value">
        R$ {{ "{:,.2f}".format(data["Custos com Produtos e Serviços"]) }}
      </div>
      <div class="metric-percent">
        {{ data["Representatividade CMV (%)"] }}%
      </div>
    </div>

    <!-- card 4 -->
    <div class="metric-card">
      <div class="metric-icon">
        <img src="data:image/png;base64,{{ icon_png_b64_4 }}"
             width="45" height="45" alt="Ícone Despesas"/>
      </div>
      <div class="metric-label">Despesas Fixas</div>
      <div class="metric-value">
        R$ {{ "{:,.2f}".format(data["Despesas Fixas"]) }}
      </div>
      <div class="metric-percent">
        {{ data["Representatividade Despesas Fixas (%)"] }}%
      </div>
    </div>

  </div>

<div class="metrics-row">
  <!-- card 5 -->
  <div class="metric-card">
    <div class="metric-icon">
      {% if data["EBITDA"] < 0 %}
        <img src="data:image/png;base64,{{ icon_png_b64_2 }}"
             width="50" height="50" alt="Ícone EBITDA Negativo"/>
      {% else %}
        <img src="data:image/png;base64,{{ icon_png_b64_5 }}"
             width="50" height="50" alt="Ícone EBITDA Positivo"/>
      {% endif %}
    </div>
    <div class="metric-label">EBITDA</div>
    <div class="metric-value">
      R$ {{ "{:,.2f}".format(data["EBITDA"]) }}
    </div>
    <div class="metric-percent">
      {{ data["Representatividade EBITDA (%)"] }}%
    </div>
  </div>

  <!-- card 6 -->
  <div class="metric-card metric-card--operacional">
    <div class="metric-icon">
      {% if data["Lucro Operacional"] < 0 %}
        <img src="data:image/png;base64,{{ icon_png_b64_2 }}"
             width="50" height="50" alt="Ícone Lucro Operacional Negativo"/>
      {% else %}
        <img src="data:image/png;base64,{{ icon_png_b64_5 }}"
             width="50" height="50" alt="Ícone Lucro Operacional Positivo"/>
      {% endif %}
    </div>
    <div class="metric-label">Lucro Operacional</div>
    <div class="metric-value">
      R$ {{ "{:,.2f}".format(data["Lucro Operacional"]) }}
    </div>
    <div class="metric-percent">
      {{ data["Representatividade Lucro Operacional (%)"] }}%
    </div>
  </div>

  <!-- card 7 -->
  <div class="metric-card">
    <div class="metric-icon">
      {% if data["Lucro Líquido"] < 0 %}
        <img src="data:image/png;base64,{{ icon_png_b64_2 }}"
             width="50" height="50" alt="Ícone Lucro Líquido Negativo"/>
      {% else %}
        <img src="data:image/png;base64,{{ icon_png_b64_5 }}"
             width="50" height="50" alt="Ícone Lucro Líquido Positivo"/>
      {% endif %}
    </div>
    <div class="metric-label">Lucro Líquido</div>
    <div class="metric-value">
      R$ {{ "{:,.2f}".format(data["Lucro Líquido"]) }}
    </div>
    <div class="metric-percent">
      {{ data["Representatividade Lucro Líquido (%)"] }}%
    </div>
  </div>
</div>

<div class="notes-title">Notas</div>
  <div class="box-frame">
    <div class="notes-content">{{ data.notas }}</div>
</div>

</div>
</body>
</html>
'''
    template = Template(template_str)
    html = template.render(
        data          = data,
        dre_items     = dre_items,
        range_total   = range_total,
        negative_total= negative_total,
        icon_rodape    = icon_rodape,
        icon_png_b64 = icon_png_b64,
        icon_png_b64_2 = icon_png_b64_2,
        icon_png_b64_3 = icon_png_b64_3,
        icon_png_b64_4 = icon_png_b64_4,
        icon_png_b64_5 = icon_png_b64_5,
        chart_base64    = chart_base64,
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
    notas = st.text_area("Notas", "", help="Digite notas do relatório (quebras de linha preservadas)")

    # Categorias DRE
    faturamento = st.number_input("Faturamento", min_value=0.0, format="%.2f")
    custos_e_deducoes = st.number_input("Custos e Deduções", max_value=0.0, format="%.2f")
    deducoes = st.number_input("Deduções da receita bruta", max_value=0.0, format="%.2f")
    cmv = st.number_input("Custos com Produtos e Serviços", max_value=0.0, format="%.2f")
    custosvariaveis = st.number_input("Custos Variáveis", max_value=0.0, format="%.2f")
    despesasfixas = st.number_input("Despesas Fixas", max_value=0.0, format="%.2f")
    ebitda = st.number_input("EBITDA", format="%.2f")
    lucro_operacional = st.number_input("Lucro Operacional", format="%.2f")
    lucro_liquido = st.number_input("Lucro Líquido", format="%.2f")

    # Representatividades
    represent_faturamento = st.number_input("Representatividade Faturamento (%)", min_value=0.0, max_value=100.0, format="%.2f")
    represent_custos_e_deducoes = st.number_input("Representatividade Custos e Deduções (%)", min_value=0.0, max_value=100.0, format="%.2f")
    represent_cmv = st.number_input("Representatividade CMV (%)", min_value=0.0, max_value=100.0, format="%.2f")
    represent_despesasfixas = st.number_input("Representatividade Despesas Fixas (%)", min_value=0.0, max_value=100.0, format="%.2f")
    represent_ebitda = st.number_input("Representatividade EBITDA (%)", min_value=0.0, max_value=100.0, format="%.2f")
    represent_lucro_operacional = st.number_input("Representatividade Lucro Operacional (%)", min_value=0.0, max_value=100.0, format="%.2f")
    represent_lucro_liquido = st.number_input("Representatividade Lucro Líquido (%)", min_value=0.0, max_value=100.0, format="%.2f")

    # Gerar e baixar PDF
    if st.button("Gerar PDF"):
        data = {
            "nome": nome,
            "Periodo": periodo,
            "notas": notas,

            "Faturamento": faturamento,
            "Deduções": deducoes,
            "Custos Variáveis": custosvariaveis,
            "Despesas Fixas": despesasfixas,
            "EBITDA": ebitda,

            "Custos e Deduções": custos_e_deducoes,
            "Custos com Produtos e Serviços": cmv,
            "Lucro Operacional": lucro_operacional,
            "Lucro Líquido": lucro_liquido,

            "Representatividade Faturamento (%)": represent_faturamento,
            "Representatividade Custos e Deduções (%)": represent_custos_e_deducoes,
            "Representatividade CMV (%)": represent_cmv,
            "Representatividade Despesas Fixas (%)": represent_despesasfixas,
            "Representatividade EBITDA (%)": represent_ebitda,
            "Representatividade Lucro Operacional (%)": represent_lucro_operacional,
            "Representatividade Lucro Líquido (%)": represent_lucro_liquido
        }
        pdf = render_pdf(data)
        st.download_button("Baixar Relatório PDF",
                           data=pdf,
                           file_name="relatorio.pdf",
                           mime="application/pdf")

if __name__ == "__main__":
    main()