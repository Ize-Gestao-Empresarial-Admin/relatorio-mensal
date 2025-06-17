import os
import base64
import json
import io
import numpy as np
import matplotlib.pyplot as plt
import textwrap
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib.patches import Rectangle
from jinja2 import Environment, FileSystemLoader

def y_fmt(value, tick_number):
    """Formata os valores do eixo Y do gráfico."""
    abs_val = abs(value)
    if abs_val >= 1_000_000:
        return f"{value/1_000_000:.0f}M"
    elif abs_val >= 1_000:
        return f"{value/1_000:.0f}k"
    else:
        return f"{value:.0f}"

def make_waterfall_base64(dre_items):
    """Gera o gráfico waterfall em base64."""
    labels = [d["label"] for d in dre_items]
    values = [d["value"] for d in dre_items]
    bottoms = [0]
    for v in values[:-1]:
        bottoms.append(bottoms[-1] + v)

    fig, ax = plt.subplots(figsize=(8, 4), dpi=300)
    bar_width = 0.6
    colors = ['#009F64' if v >= 0 else '#FF6900' for v in values]

    cumul = [0]
    for v in values:
        cumul.append(cumul[-1] + v)
    for i in range(len(values)-1):
        y = cumul[i+1]
        x1 = i + bar_width/2
        x2 = (i+1) - bar_width/2
        ax.hlines(y, x1, x2, colors="#CCCCCC", linestyles="--", linewidth=1, zorder=0)

    ax.axhline(0, color="#E5E5E5", linewidth=1, zorder=0)

    for i, (val, bot, col) in enumerate(zip(values, bottoms, colors)):
        if val >= 0:
            y, height = bot, val
        else:
            y, height = bot + val, -val
        x = i - bar_width/2
        rect = Rectangle(
            (x, y), bar_width, height, facecolor=col, edgecolor=col,
            linewidth=5, joinstyle='round', zorder=1
        )
        ax.add_patch(rect)

    ax.grid(False)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#69696F")
    ax.spines["left"].set_color("#69696F")
    ax.spines["bottom"].set_linewidth(0.5)
    ax.spines["left"].set_linewidth(0.5)

    wrapped = ["\n".join(textwrap.wrap(l, width=15)) for l in labels]
    ax.set_xticks(range(len(wrapped)))
    ax.set_xlim(-0.5, len(wrapped)-0.5)
    ax.set_xticklabels(wrapped, rotation=0, ha="center", fontsize=10)
    ax.tick_params(axis='both', which='major', length=0, labelcolor="#69696F", pad=12)
    ax.spines['bottom'].set_position(('outward', 10))
    ax.xaxis.set_ticks_position('bottom')
    ax.margins(y=0.05)

    x0_data = 0
    xlim = ax.get_xlim()
    x0_frac = (x0_data - xlim[0]) / (xlim[1] - xlim[0])
    ax.vlines(
        x=x0_frac-0.1, ymin=-0.046, ymax=0, transform=ax.transAxes,
        colors="#69696F", linewidth=0.5, clip_on=False
    )

    ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))
    ax.yaxis.set_major_locator(MaxNLocator(6))

    fig.subplots_adjust(bottom=0.25)
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=800)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def criar_html_teste_relatorio6(output_file="templates/preview_relatorio6.html"):
    """
    Cria uma versão de teste do template HTML do Relatório 6 com dados fictícios para visualização.
    
    Args:
        output_file: Caminho onde o HTML de teste será salvo
    """
    # Configurar o ambiente Jinja2
    env = Environment(loader=FileSystemLoader('.'))
    
    # Registrar os filtros personalizados
    def format_currency(value):
        if value is None:
            return "R$ 0,00"
        try:
            return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return value
    
    def format_percentage(value):
        if value is None:
            return "0%"
        try:
            return f"{value:.1%}".replace(".", ",")
        except:
            return value
    
    def format_number(value, decimal_places=2):
        if value is None:
            return "0"
        try:
            format_str = f"{{:.{decimal_places}f}}"
            return format_str.format(value).replace(".", ",")
        except:
            return value
    
    # Adicionar os filtros ao ambiente
    env.filters['format_currency'] = format_currency
    env.filters['format_percentage'] = format_percentage
    env.filters['format_number'] = format_number
    
    # Carregar o template
    template = env.get_template("templates/relatorio6/template.html")
    
    # Carregar ícones e imagens
    icons_dir = os.path.abspath("assets/icons")
    
    # Carregar o rodapé
    rodape_path = os.path.join(icons_dir, "rodape.png")
    try:
        with open(rodape_path, "rb") as f:
            icon_bytes = f.read()
            icon_rodape = base64.b64encode(icon_bytes).decode("ascii")
    except Exception as e:
        print(f"Erro ao carregar rodapé: {str(e)}")
        icon_rodape = ""
    
    # Carregar ícones para os cards
    icon_paths = {
        "faturamento": os.path.join(icons_dir, "LOGO-FATURAMENTO.png"),
        "lucro_laranja": os.path.join(icons_dir, "LOGO-LUCRO-LARANJA.png"),
        "cmv": os.path.join(icons_dir, "LOGO-CMV.png"),
        "despesas": os.path.join(icons_dir, "LOGO-DESPESAS.png"),
        "lucro_verde": os.path.join(icons_dir, "LOGO-LUCRO-VERDE.png")
    }
    
    icons_base64 = {}
    for name, path in icon_paths.items():
        try:
            with open(path, "rb") as f:
                icon_bytes = f.read()
                icons_base64[name] = base64.b64encode(icon_bytes).decode("ascii")
        except Exception as e:
            print(f"Erro ao carregar ícone {name}: {str(e)}")
            icons_base64[name] = ""

    # Dados fictícios para o DRE
    dados_teste = {
        "nome": "Cliente Exemplo",
        "Periodo": "Junho/2024",
        "notas": "Este é um demonstrativo de resultado do exercício (DRE) que apresenta os principais indicadores financeiros da empresa para o período.\n\nNo mês, tivemos um total de vendas no montante de R$ 950.000,00, seguido das deduções da receita bruta de R$ 95.000,00, Custos Variáveis em R$ 285.000,00, Despesas Fixas de R$ 380.000,00, fechando o mês com um EBITDA de 20,0% em relação ao faturamento!",
        "Faturamento": 950000.00,
        "Deduções": -95000.00,
        "Custos Variáveis": -285000.00,
        "Despesas Fixas": -380000.00,
        "EBITDA": 190000.00,
        "Custos e Deduções": -380000.00,
        "Custos com Produtos e Serviços": -285000.00,
        "Lucro Operacional": 171000.00,
        "Lucro Líquido": 138000.00,
        "Representatividade Faturamento (%)": 1.0,
        "Representatividade Custos e Deduções (%)": 0.4,
        "Representatividade CMV (%)": 0.3,
        "Representatividade Despesas Fixas (%)": 0.4,
        "Representatividade EBITDA (%)": 0.2,
        "Representatividade Lucro Operacional (%)": 0.18,
        "Representatividade Lucro Líquido (%)": 0.145
    }

    # Preparar itens para o gráfico Waterfall
    dre_items = [
        {"label": "Faturamento", "value": dados_teste["Faturamento"]},
        {"label": "Deduções da receita bruta", "value": dados_teste["Deduções"]},
        {"label": "Custos Variáveis", "value": dados_teste["Custos Variáveis"]},
        {"label": "Despesas Fixas", "value": dados_teste["Despesas Fixas"]},
        {"label": "EBITDA", "value": dados_teste["EBITDA"]},
    ]

    # Gerar gráfico Waterfall
    chart_base64 = make_waterfall_base64(dre_items)

    # Renderizar template
    try:
        html = template.render(
            data=dados_teste,
            icon_rodape=icon_rodape,
            icon_png_b64=icons_base64["faturamento"],
            icon_png_b64_2=icons_base64["lucro_laranja"],
            icon_png_b64_3=icons_base64["cmv"],
            icon_png_b64_4=icons_base64["despesas"],
            icon_png_b64_5=icons_base64["lucro_verde"],
            chart_base64=chart_base64,
            cliente_nome=dados_teste["nome"],
            mes_nome="Junho",
            ano=2024
        )
        
        # Salvar o HTML para visualização
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"HTML de teste do Relatório 6 criado com sucesso em: {output_file}")
        print(f"Abra este arquivo no navegador para visualização.")
        return True
    except Exception as e:
        print(f"Erro ao renderizar template do Relatório 6: {str(e)}")
        return False

def criar_servidor_teste():
    """
    Inicia um servidor HTTP simples para visualizar o template do Relatório 6
    """
    import http.server
    import socketserver
    
    # Criar o HTML de teste
    if not criar_html_teste_relatorio6():
        print("Não foi possível criar o HTML de teste do Relatório 6. Servidor não iniciado.")
        return
    
    # Configurar o servidor
    PORT = 8006
    Handler = http.server.SimpleHTTPRequestHandler
    
    print(f"Iniciando servidor na porta {PORT}...")
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Servidor rodando em http://localhost:{PORT}")
            print(f"Acesse http://localhost:{PORT}/templates/preview_relatorio6.html para visualizar o Relatório 6")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuário.")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Ferramentas de teste para o template do Relatório 6')
    parser.add_argument('--serve', action='store_true', help='Iniciar servidor HTTP para visualização')
    parser.add_argument('--output', type=str, help='Caminho para salvar o arquivo HTML', default="templates/preview_relatorio6.html")
    
    args = parser.parse_args()
    
    if args.serve:
        criar_servidor_teste()
    else:
        criar_html_teste_relatorio6(args.output)
        print("Para iniciar um servidor HTTP para testes, use: python template_relatorio6_test.py --serve")