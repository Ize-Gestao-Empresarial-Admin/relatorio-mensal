# src/rendering/renderers/relatorio6_renderer.py
from typing import Dict, Any, List, Tuple, Union
from src.rendering.renderers.base_renderer import BaseRenderer
import matplotlib.pyplot as plt
import textwrap
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib.patches import Rectangle
import base64
import os
import io
import numpy as np

class Relatorio6Renderer(BaseRenderer):
    """Renderizador específico para o Relatório 6 - Indicadores DRE."""

    def __init__(self):
        super().__init__()
        # Carregar o template do relatório 6
        self.template = self.env.get_template("relatorio6/template.html")

    def y_fmt(self, value, tick_number):
        """Formata os valores do eixo Y do gráfico."""
        abs_val = abs(value)
        if abs_val >= 1_000_000:
            return f"{value/1_000_000:.0f}M"
        elif abs_val >= 1_000:
            return f"{value/1_000:.0f}k"
        else:
            return f"{value:.0f}"

    def make_waterfall_base64(self, dre_items):
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

        ax.yaxis.set_major_formatter(FuncFormatter(self.y_fmt))
        ax.yaxis.set_major_locator(MaxNLocator(6))

        fig.subplots_adjust(bottom=0.25)
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=800)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    def load_icon(self, icon_path: str) -> str:
        """Carrega um ícone em base64."""
        try:
            with open(icon_path, "rb") as f:
                icon_bytes = f.read()
            return base64.b64encode(icon_bytes).decode("ascii")
        except FileNotFoundError:
            raise FileNotFoundError(f"Ícone não encontrado: {icon_path}")

    def prepare_data(self, indicadores: List[Dict[str, Any]], notas: Dict[str, str], cliente_nome: str, mes_nome: str, ano: int) -> Dict[str, Any]:
        """Prepara os dados para renderização."""
        # Mapeamento dos indicadores
        indicadores_dict = {item["indicador"]: item for item in indicadores}

        # Verificar se todos os valores são nulos, zero ou NaN
        all_null_or_zero = all(
            item["valor"] == 0 or np.isnan(item["valor"]) or item["valor"] is None
            for item in indicadores
        )

        # Preparar notas automatizadas
        if all_null_or_zero:
            notas_automatizadas = "Não há dados disponíveis para o período selecionado."
        else:
            faturamento = indicadores_dict.get("Faturamento", {}).get("valor", 0.0)
            deducoes = indicadores_dict.get("Deduções da Receita Bruta", {}).get("valor", 0.0)
            custos_variaveis = indicadores_dict.get("Custos Variáveis", {}).get("valor", 0.0)
            despesas_fixas = indicadores_dict.get("Despesas Fixas", {}).get("valor", 0.0)
            notas_automatizadas = (
                f"No mês, tivemos um total de vendas no montante de R$ {faturamento:,.2f}, "
                f"seguido das deduções da receita bruta de R$ {deducoes:,.2f}, "
                f"Custos Variáveis em R$ {custos_variaveis:,.2f}, "
                f"Despesas Fixas de R$ {despesas_fixas:,.2f}, "
                f"fechando o mês com um EBITDA de {indicadores_dict.get('EBITDA', {}).get('av_dre', 0.0)}% em relação ao faturamento!"
            )

        # Dados para o template
        data = {
            "nome": cliente_nome,
            "Periodo": f"{mes_nome}/{ano}",
            "notas": notas.get("notas", notas_automatizadas),
            "Faturamento": indicadores_dict.get("Faturamento", {}).get("valor", 0.0),
            "Deduções": indicadores_dict.get("Deduções da Receita Bruta", {}).get("valor", 0.0),
            "Custos Variáveis": indicadores_dict.get("Custos Variáveis", {}).get("valor", 0.0),
            "Despesas Fixas": indicadores_dict.get("Despesas Fixas", {}).get("valor", 0.0),
            "EBITDA": indicadores_dict.get("EBITDA", {}).get("valor", 0.0),
            "Custos e Deduções": indicadores_dict.get("Custos Variáveis + Deduções da Receita", {}).get("valor", 0.0),
            "Custos com Produtos e Serviços": indicadores_dict.get("Custos com Produtos e Serviços", {}).get("valor", 0.0),
            "Lucro Operacional": indicadores_dict.get("Lucro Operacional", {}).get("valor", 0.0),
            "Lucro Líquido": indicadores_dict.get("Lucro Líquido", {}).get("valor", 0.0),
            "Representatividade Faturamento (%)": indicadores_dict.get("Faturamento", {}).get("av_dre", 0.0),
            "Representatividade Custos e Deduções (%)": indicadores_dict.get("Custos Variáveis + Deduções da Receita", {}).get("av_dre", 0.0),
            "Representatividade CMV (%)": indicadores_dict.get("Custos com Produtos e Serviços", {}).get("av_dre", 0.0),
            "Representatividade Despesas Fixas (%)": indicadores_dict.get("Despesas Fixas", {}).get("av_dre", 0.0),
            "Representatividade EBITDA (%)": indicadores_dict.get("EBITDA", {}).get("av_dre", 0.0),
            "Representatividade Lucro Operacional (%)": indicadores_dict.get("Lucro Operacional", {}).get("av_dre", 0.0),
            "Representatividade Lucro Líquido (%)": indicadores_dict.get("Lucro Líquido", {}).get("av_dre", 0.0),
        }
        return data

    def render(self, data: Union[List[Dict[str, Any]], Tuple[List[Dict[str, Any]], Dict[str, str]]], 
               cliente_nome: str, mes_nome: str, ano: int) -> str:
        """
        Renderiza os indicadores operacionais em HTML.

        Args:
            data: Lista de indicadores ou tupla com indicadores e notas.
            cliente_nome: Nome do cliente.
            mes_nome: Nome do mês.
            ano: Ano do relatório.

        Returns:
            HTML formatado.
        """
        # Extrair dados na estrutura correta
        if isinstance(data, tuple):
            indicadores, notas = data
        else:
            indicadores, notas = data, {"notas": ""}

        # Preparar os dados
        data_prepared = self.prepare_data(indicadores, notas, cliente_nome, mes_nome, ano)

        # Preparar itens para o gráfico Waterfall
        dre_items = [
            {"label": "Faturamento", "value": data_prepared["Faturamento"]},
            {"label": "Deduções da receita bruta", "value": data_prepared["Deduções"]},
            {"label": "Custos Variáveis", "value": data_prepared["Custos Variáveis"]},
            {"label": "Despesas Fixas", "value": data_prepared["Despesas Fixas"]},
            {"label": "EBITDA", "value": data_prepared["EBITDA"]},
        ]

        # Gerar gráfico Waterfall
        chart_base64 = self.make_waterfall_base64(dre_items)

        # Carregar ícones
        icons_dir = os.path.abspath("assets/icons")
        icon_rodape = self.load_icon(os.path.join(icons_dir, "rodape.png"))
        icon_png_b64 = self.load_icon(os.path.join(icons_dir, "LOGO-FATURAMENTO.png"))
        icon_png_b64_2 = self.load_icon(os.path.join(icons_dir, "LOGO-LUCRO-LARANJA.png"))
        icon_png_b64_3 = self.load_icon(os.path.join(icons_dir, "LOGO-CMV.png"))
        icon_png_b64_4 = self.load_icon(os.path.join(icons_dir, "LOGO-DESPESAS.png"))
        icon_png_b64_5 = self.load_icon(os.path.join(icons_dir, "LOGO-LUCRO-VERDE.png"))
        
        #Renderizar o template
        return self.template.render(
            data=data_prepared,
            icon_rodape=icon_rodape,
            icon_png_b64=icon_png_b64,
            icon_png_b64_2=icon_png_b64_2,
            icon_png_b64_3=icon_png_b64_3,
            icon_png_b64_4=icon_png_b64_4,
            icon_png_b64_5=icon_png_b64_5,
            chart_base64=chart_base64,
            cliente_nome=cliente_nome,
            mes_nome=mes_nome,
            ano=ano
        )