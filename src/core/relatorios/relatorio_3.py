# src/core/relatorios/relatorio3_.py
from datetime import date
from typing import Optional, List, Dict, Any
from src.core.indicadores import Indicadores
from dateutil.relativedelta import relativedelta
from src.core.utils import calcular_outras_categorias, safe_float

class Relatorio3:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> List[Dict[str, Any]]:
        """Gera o relatório 3 com lucro operacional, investimentos e suas representatividades.

        Args:
            mes_atual: Data do mês atual para o cálculo.
            mes_anterior: Data do mês anterior para análise horizontal (opcional).

        Returns:
            Lista de dicionários contendo categorias e subcategorias, junto com notas.
        """
        # Calcula mês anterior automaticamente se não for passado
        if mes_anterior is None:
            mes_anterior = mes_atual - relativedelta(months=1)
        
        # Chamar funções de indicadores
        lucro_operacional_resultado = self.indicadores.calcular_lucro_operacional_fc(mes_atual, mes_anterior)
        investimentos_resultado = self.indicadores.calcular_investimentos_fc(mes_atual, mes_anterior)
        lucro_operacional_anterior_resultado = self.indicadores.calcular_lucro_operacional_fc(mes_anterior, None)
        investimentos_anterior_resultado = self.indicadores.calcular_investimentos_fc(mes_anterior, None)

        # Extrair valores, tratando None explicitamente
        def get_valor(categoria: str, resultado: List[Dict[str, Any]], default: float = 0.0) -> float:
            valor = next((r['valor'] for r in resultado if r['categoria'] == categoria), default)
            return safe_float(valor, default)

        # Valores do mês atual
        receita_atual = get_valor('Receita', lucro_operacional_resultado)
        custos_variaveis_atual = get_valor('Custos Variáveis', lucro_operacional_resultado)
        despesas_fixas_atual = get_valor('Despesas Fixas', lucro_operacional_resultado)
        lucro_operacional_atual = receita_atual - custos_variaveis_atual - despesas_fixas_atual
        investimentos_atual = sum(safe_float(r['valor']) for r in investimentos_resultado)

        # Valores do mês anterior
        receita_anterior = get_valor('Receita', lucro_operacional_anterior_resultado)
        custos_variaveis_anterior = get_valor('Custos Variáveis', lucro_operacional_anterior_resultado)
        despesas_fixas_anterior = get_valor('Despesas Fixas', lucro_operacional_anterior_resultado)
        lucro_operacional_anterior = receita_anterior - custos_variaveis_anterior - despesas_fixas_anterior
        investimentos_anterior = sum(abs(safe_float(r['valor'])) for r in investimentos_anterior_resultado)

        # Calcular subcategorias com "Outras categorias" para Lucro Operacional
        lucro_operacional_categorias = calcular_outras_categorias(
            items=lucro_operacional_resultado,
            items_anterior=lucro_operacional_anterior_resultado,
            total_atual=lucro_operacional_atual,
            total_anterior=lucro_operacional_anterior,
            receita_total=receita_atual,
            chave_valor="valor",
            chave_nome="categoria",
            top_n=3,
            usar_valor_abs=False  # Ordenação natural para Receita, Custos, Despesas
        )

        # Calcular subcategorias com "Outras categorias" para Investimentos
        investimentos_categorias = calcular_outras_categorias(
            items=investimentos_resultado,
            items_anterior=investimentos_anterior_resultado,
            total_atual=investimentos_atual,
            total_anterior=investimentos_anterior,
            receita_total=receita_atual,
            chave_valor="valor",
            chave_nome="categoria",
            top_n=3,
            usar_valor_abs=True  # Ordenação por valor absoluto
        )

        # Calcula AV para lucro operacional
        lucro_operacional_av = round((lucro_operacional_atual / receita_atual * 100) if receita_atual != 0 else 0, 2)

        # Calcula AH para lucro operacional
        lucro_operacional_ah = round(
            ((lucro_operacional_atual / lucro_operacional_anterior - 1) * 100) if lucro_operacional_anterior != 0 else 0, 2
        )

        # Calcula AV para investimentos
        investimentos_av = round((investimentos_atual / receita_atual * 100) if receita_atual != 0 else 0, 2)

        # Calcula AH para investimentos
        investimentos_ah = round(
            ((investimentos_atual / investimentos_anterior - 1) * 100) if investimentos_anterior != 0 else 0, 2
        )

        # Obtém a categoria mais representativa dos investimentos
        categoria_maior_peso_investimentos = max(
            investimentos_categorias, key=lambda x: x['representatividade'], default={'subcategoria': 'N/A'}
        )['subcategoria']

        # Formata a nota automatizada
        notas_automatizadas = (
            f"O nosso principal indicador de eficiência da empresa, o Lucro Operacional, fechou em {lucro_operacional_av}% "
            f"(R$ {lucro_operacional_atual:,.2f}) em relação à Receita Total, "
            f"uma variação de {lucro_operacional_ah}% em relação ao mês anterior. "
            f"Nos investimentos, totalizamos R$ {investimentos_atual:,.2f}, {investimentos_ah}% em relação ao mês anterior, "
            f"com protagonismo da categoria {categoria_maior_peso_investimentos}."
        )

        # Verifica se não há dados relevantes
        if (not lucro_operacional_resultado or lucro_operacional_atual == 0) and \
           (not investimentos_resultado or investimentos_atual == 0):
            notas_automatizadas = "Não há dados disponíveis para o período selecionado."

        return [
            {
                "categoria": "Lucro Operacional",
                "valor": lucro_operacional_atual,
                "av_categoria": lucro_operacional_av,
                "subcategorias": lucro_operacional_categorias,
            },
            {
                "categoria": "Investimentos",
                "valor": investimentos_atual,
                "av_categoria": investimentos_av,
                "subcategorias": investimentos_categorias,
            }
        ], {
            "notas": notas_automatizadas
        }