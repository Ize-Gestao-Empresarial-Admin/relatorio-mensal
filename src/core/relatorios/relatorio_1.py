# src/core/relatorios/relatorio_1.py
from datetime import date
from typing import Optional, List, Dict, Any
from src.core.indicadores import Indicadores
from dateutil.relativedelta import relativedelta
from src.core.utils import calcular_outras_categorias, safe_float
import math

class Relatorio1:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        """Initializes the Relatorio1 class with indicators and client name."""
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente
    
    def safe_float(self, value: Any, default: float = 0.0) -> float:
        """Converts a value to float, handling NaN and None as the default value."""
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> List[Dict[str, Any]]:
        """Generates Report 1 with revenues, variable costs, and their representativeness.

        Args:
            mes_atual: Current month date for calculations.
            mes_anterior: Previous month date for horizontal analysis (optional).

        Returns:
            Tuple with a list of dictionaries (categories and subcategories) and a notes dictionary.
        """
        # Calculate previous month automatically if not provided
        if mes_anterior is None:
            mes_anterior = mes_atual - relativedelta(months=1)
        
        receitas = self.indicadores.calcular_receitas_fc(mes_atual, '3.%')
        custos = self.indicadores.calcular_custos_variaveis_fc(mes_atual, '4.%')
        receitas_mes_anterior = self.indicadores.calcular_receitas_fc(mes_anterior, '3.%')
        custos_mes_anterior = self.indicadores.calcular_custos_variaveis_fc(mes_anterior, '4.%')

        # Calculate totals
        receita_total = sum(self.safe_float(r.get('total_categoria', 0)) for r in receitas) if receitas else 0
        custos_total = sum(self.safe_float(c.get('total_categoria', 0)) for c in custos) if custos else 0
        receita_total_anterior = sum(self.safe_float(r.get('total_categoria', 0)) for r in receitas_mes_anterior) if receitas_mes_anterior else 0
        custos_total_anterior = sum(self.safe_float(c.get('total_categoria', 0)) for c in custos_mes_anterior) if custos_mes_anterior else 0

        # Calculate subcategories with "Outras categorias" for Receitas
        receitas_categoria = calcular_outras_categorias(
            items=receitas,
            items_anterior=receitas_mes_anterior,
            total_atual=receita_total,
            total_anterior=receita_total_anterior,
            receita_total=receita_total,  # Pass receita_total for AV calculation
            chave_valor="total_categoria",
            chave_nome="categoria_nivel_3",
            top_n=3,
            usar_valor_abs=False
        )

        # Calculate subcategories with "Outras categorias" for Custos Variáveis
        custos_variaveis = calcular_outras_categorias(
            items=custos,
            items_anterior=custos_mes_anterior,
            total_atual=custos_total,
            total_anterior=custos_total_anterior,
            receita_total=receita_total,  # Pass receita_total for AV calculation
            chave_valor="total_categoria",
            chave_nome="nivel_2",
            top_n=3,
            usar_valor_abs=True
        )

        # Identify the most representative categories
        receitas_ordenadas = sorted(receitas_categoria, key=lambda x: x['representatividade'], reverse=True)
        primeira_cat_receita = receitas_ordenadas[0]['subcategoria'] if len(receitas_ordenadas) > 0 else "N/A"
        segunda_cat_receita = receitas_ordenadas[1]['subcategoria'] if len(receitas_ordenadas) > 1 else "N/A"
        custos_ordenados = sorted(custos_variaveis, key=lambda x: x['representatividade'], reverse=True)
        primeira_cat_custo = custos_ordenados[0]['subcategoria'] if len(custos_ordenados) > 0 else "N/A"

        # Calculate AH for total revenue
        receita_total_ah = round(
            ((receita_total / receita_total_anterior) - 1) * 100, 2
        ) if receita_total_anterior != 0 else 0

        # Format automated notes
        notas_automatizadas = (
            f"No mês, observamos uma receita operacional de R$ {receita_total:,.2f}, "
            f"uma variação de {receita_total_ah}% em relação ao mês anterior, "
            f"com principal peso na categoria {primeira_cat_receita} e {segunda_cat_receita}. "
            f"Em relação aos custos variáveis, tivemos um resultado de R$ {custos_total:,.2f}, "
            f"com destaque para {primeira_cat_custo}."
        )

        # Check if there are valid data
        if (not receitas or all(self.safe_float(r.get("total_categoria", 0)) == 0 for r in receitas)) and \
           (not custos or all(self.safe_float(c.get("total_categoria", 0)) == 0 for c in custos)):
            notas_automatizadas = "Não há dados disponíveis para o período selecionado."

        return [
            {
                "categoria": "Receitas",
                "valor": receita_total,
                "subcategorias": receitas_categoria,
            },
            {
                "categoria": "Custos Variáveis",
                "valor": custos_total,
                "subcategorias": custos_variaveis,
            }
        ], {
            "notas": notas_automatizadas
        }