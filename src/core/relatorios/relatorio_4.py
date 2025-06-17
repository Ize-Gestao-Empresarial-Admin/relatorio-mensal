# src/core/relatorios/relatorio4.py
from datetime import date
from typing import Optional, List, Dict, Any
import math
from dateutil.relativedelta import relativedelta
from src.core.indicadores import Indicadores
from src.core.utils import calcular_outras_categorias, safe_float

class Relatorio4:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> List[Dict[str, Any]]:
        """Gera o relatório 4 com lucro líquido, entradas e resultados não operacionais.

        Args:
            mes_atual: Data do mês atual para o cálculo.
            mes_anterior: Data do mês anterior para análise horizontal (opcional).

        Returns:
            Lista de dicionários contendo categorias e subcategorias, junto com notas.
        """
        # Calcula mês anterior automaticamente se não for passado
        if mes_anterior is None:
            mes_anterior = mes_atual - relativedelta(months=1)

        # Chamar funções de indicadores para o mês atual
        lucro_liquido_resultado = self.indicadores.calcular_lucro_liquido_fc(mes_atual)
        entradas_nao_operacionais_resultado = self.indicadores.calcular_entradas_nao_operacionais_fc(mes_atual)
        resultados_nao_operacionais_resultado = self.indicadores.calcular_resultados_nao_operacionais_fc(mes_atual)

        # Chamar funções de indicadores para o mês anterior
        lucro_liquido_anterior_resultado = self.indicadores.calcular_lucro_liquido_fc(mes_anterior)
        entradas_nao_operacionais_anterior_resultado = self.indicadores.calcular_entradas_nao_operacionais_fc(mes_anterior)
        resultados_nao_operacionais_anterior_resultado = self.indicadores.calcular_resultados_nao_operacionais_fc(mes_anterior)

        # Extrair valores, tratando None e NaN
        def get_valor(categoria: str, resultado: List[Dict[str, Any]], default: float = 0.0) -> float:
            valor = next((r['valor'] for r in resultado if r['categoria'] == categoria), default)
            return safe_float(valor, default)

        # Valores do mês atual
        receita_atual = get_valor('Receita', lucro_liquido_resultado)
        custos_variaveis_atual = get_valor('Custos Variáveis', lucro_liquido_resultado)
        despesas_fixas_atual = get_valor('Despesas Fixas', lucro_liquido_resultado)
        investimentos_atual = get_valor('Investimentos', lucro_liquido_resultado)
        lucro_liquido_atual = safe_float(receita_atual - custos_variaveis_atual - despesas_fixas_atual - investimentos_atual)

        entradas_nao_operacionais_total = sum(safe_float(e["total_valor"]) for e in entradas_nao_operacionais_resultado)
        resultados_nao_operacionais_total = sum(safe_float(r["total_valor"]) for r in resultados_nao_operacionais_resultado)

        # Valores do mês anterior
        receita_anterior = get_valor('Receita', lucro_liquido_anterior_resultado)
        lucro_liquido_anterior = safe_float(
            receita_anterior - 
            get_valor('Custos Variáveis', lucro_liquido_anterior_resultado) - 
            get_valor('Despesas Fixas', lucro_liquido_anterior_resultado) - 
            get_valor('Investimentos', lucro_liquido_anterior_resultado)
        )
        entradas_nao_operacionais_anterior_total = sum(safe_float(e["total_valor"]) for e in entradas_nao_operacionais_anterior_resultado)
        resultados_nao_operacionais_anterior_total = sum(safe_float(r["total_valor"]) for r in resultados_nao_operacionais_anterior_resultado)

        # Calcular subcategorias com "Outras categorias"
        lucro_liquido_categorias = calcular_outras_categorias(
            items=lucro_liquido_resultado,
            items_anterior=lucro_liquido_anterior_resultado,
            total_atual=lucro_liquido_atual,
            total_anterior=lucro_liquido_anterior,
            receita_total=receita_atual,
            chave_valor="valor",
            chave_nome="categoria",
            top_n=4,  # Alterado de 3 para 4 para incluir todas as categorias: Receita, Custos Variáveis, Despesas Fixas, Investimentos
            usar_valor_abs=False  # Ordenação natural para Receita, Custos, Despesas, Investimentos
        )

        entradas_nao_operacionais_categorias = calcular_outras_categorias(
            items=[{"categoria_nivel_3": e["categoria_nivel_3"], "valor": e["total_valor"], "av": e["av"], "ah": e["ah"]} 
                   for e in entradas_nao_operacionais_resultado],
            items_anterior=[{"categoria_nivel_3": e["categoria_nivel_3"], "valor": e["total_valor"], "av": e["av"], "ah": e["ah"]} 
                            for e in entradas_nao_operacionais_anterior_resultado],
            total_atual=entradas_nao_operacionais_total,
            total_anterior=entradas_nao_operacionais_anterior_total,
            receita_total=receita_atual,
            chave_valor="valor",
            chave_nome="categoria_nivel_3",
            top_n=3,
            usar_valor_abs=True  # Ordenação por valor absoluto
        )

        resultados_nao_operacionais_categorias = calcular_outras_categorias(
            items=[{"nivel_1": r["nivel_1"], "valor": r["total_valor"], "av": r["av"], "ah": r["ah"]} 
                   for r in resultados_nao_operacionais_resultado],
            items_anterior=[{"nivel_1": r["nivel_1"], "valor": r["total_valor"], "av": r["av"], "ah": r["ah"]} 
                            for r in resultados_nao_operacionais_anterior_resultado],
            total_atual=resultados_nao_operacionais_total,
            total_anterior=resultados_nao_operacionais_anterior_total,
            receita_total=receita_atual,
            chave_valor="valor",
            chave_nome="nivel_1",
            top_n=3,
            usar_valor_abs=True  # Ordenação por valor absoluto
        )

        # Identificar a subcategoria mais representativa
        primeira_cat_entradas = max(
            entradas_nao_operacionais_categorias, key=lambda x: x['representatividade'], default={'subcategoria': 'N/A'}
        )['subcategoria']
        primeira_cat_resultado = max(
            resultados_nao_operacionais_categorias, key=lambda x: x['representatividade'], default={'subcategoria': 'N/A'}
        )['subcategoria']

        # Calcular AV e AH para as categorias
        av_lucro_liquido = round(safe_float((lucro_liquido_atual / receita_atual) * 100), 2) if receita_atual else 0
        av_entradas_nao_operacionais = round(safe_float((entradas_nao_operacionais_total / receita_atual) * 100), 2) if receita_atual else 0
        av_resultados_nao_operacionais = round(safe_float((resultados_nao_operacionais_total / receita_atual) * 100), 2) if receita_atual else 0

        lucro_liquido_ah = round(
            safe_float(((lucro_liquido_atual / lucro_liquido_anterior - 1) * 100)), 2) if lucro_liquido_anterior != 0 else 0
        entradas_ah = round(
            safe_float(((entradas_nao_operacionais_total / entradas_nao_operacionais_anterior_total - 1) * 100)), 2
        ) if entradas_nao_operacionais_anterior_total != 0 else 0
        resultados_ah = round(
            safe_float(((resultados_nao_operacionais_total / resultados_nao_operacionais_anterior_total - 1) * 100)), 2
        ) if resultados_nao_operacionais_anterior_total != 0 else 0

        # Notas automatizadas
        notas_automatizadas = (
            f"Já o Lucro Líquido, dados os indicadores anteriores, fechou em R$ {lucro_liquido_atual:,.2f} "
            f"({av_lucro_liquido}% da Receita Total), uma variação de {lucro_liquido_ah}% em relação ao mês anterior. "
            f"As Entradas Não Operacionais fecharam com R$ {entradas_nao_operacionais_total:,.2f} "
            f"({av_entradas_nao_operacionais}% da Receita Total), "
            f"com peso mais concentrado na categoria {primeira_cat_entradas}. "
            f"O Resultado Não Operacional fechou em R$ {resultados_nao_operacionais_total:,.2f} "
            f"({av_resultados_nao_operacionais}% da Receita Total), "
            f"com peso mais concentrado na categoria {primeira_cat_resultado}."
        )

        # Verifica se não há dados relevantes
        if (not lucro_liquido_resultado or lucro_liquido_atual == 0) and \
           (not entradas_nao_operacionais_resultado or entradas_nao_operacionais_total == 0) and \
           (not resultados_nao_operacionais_resultado or resultados_nao_operacionais_total == 0):
            notas_automatizadas = "Não há dados disponíveis para o período selecionado."

        return [
            {
                "categoria": "Lucro Líquido",
                "valor": lucro_liquido_atual,
                "av_categoria": av_lucro_liquido,
                "subcategorias": lucro_liquido_categorias,
            },
            {
                "categoria": "Entradas Não Operacionais",
                "valor": entradas_nao_operacionais_total,
                "av_categoria": av_entradas_nao_operacionais,
                "subcategorias": entradas_nao_operacionais_categorias,
            },
            {
                "categoria": "Resultados Não Operacionais",
                "valor": resultados_nao_operacionais_total,
                "av_categoria": av_resultados_nao_operacionais,
                "subcategorias": resultados_nao_operacionais_categorias,
            }
        ], {
            "notas": notas_automatizadas
        }