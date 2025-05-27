from datetime import date
from typing import Optional, List, Dict, Any
import math  # Importado para verificar NaN

from src.core.indicadores import Indicadores

class Relatorio4:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def safe_float(self, value: Any, default: float = 0.0) -> float:
        """Converte um valor para float, tratando NaN e None como o valor padrão."""
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return default
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> List[Dict[str, Any]]:
        # Calcular mes_anterior se não fornecido
        if mes_anterior is None:
            mes_anterior = date(mes_atual.year if mes_atual.month > 1 else mes_atual.year - 1,
                                mes_atual.month - 1 if mes_atual.month > 1 else 12, 1)

        # Chamar funções de indicadores
        lucro_liquido_resultado = self.indicadores.calcular_lucro_liquido_fc(mes_atual)
        entradas_nao_operacionais_resultado = self.indicadores.calcular_entradas_nao_operacionais_fc(mes_atual)
        resultados_nao_operacionais = self.indicadores.calcular_resultados_nao_operacionais_fc(mes_atual)

        # Extrair valores, tratando None e NaN explicitamente
        def get_valor(categoria: str, resultado: List[Dict[str, Any]], default: float = 0.0) -> float:
            valor = next((r['valor'] for r in resultado if r['categoria'] == categoria), default)
            return self.safe_float(valor, default)

        receita_atual = get_valor('Receita', lucro_liquido_resultado)
        custos_variaveis_atual = get_valor('Custos Variáveis', lucro_liquido_resultado)
        despesas_fixas_atual = get_valor('Despesas Fixas', lucro_liquido_resultado)
        investimentos_atual = get_valor('Investimentos', lucro_liquido_resultado)
        lucro_liquido_atual = self.safe_float(receita_atual - custos_variaveis_atual - despesas_fixas_atual - investimentos_atual)

        entradas_nao_operacionais_total = sum(self.safe_float(e["total_valor"]) for e in entradas_nao_operacionais_resultado) if entradas_nao_operacionais_resultado else 0
        resultados_nao_operacionais_total = sum(self.safe_float(r["total_valor"]) for r in resultados_nao_operacionais) if resultados_nao_operacionais else 0

        # Análise Vertical (AV) do Lucro Líquido
        av_lucro_liquido = self.safe_float((lucro_liquido_atual / receita_atual) * 100, 0) if receita_atual else 0
        av_lucro_liquido = round(av_lucro_liquido, 2)

        # Calcular soma total para representatividade (usar valores absolutos para evitar problemas com negativos)
        lucro_liquido_subcategorias_total = sum(abs(self.safe_float(r["valor"])) for r in lucro_liquido_resultado) if lucro_liquido_resultado else 0
        entradas_nao_operacionais_subcategorias_total = sum(abs(self.safe_float(e["total_valor"])) for e in entradas_nao_operacionais_resultado) if entradas_nao_operacionais_resultado else 0
        resultados_nao_operacionais_subcategorias_total = sum(abs(self.safe_float(r["total_valor"])) for r in resultados_nao_operacionais) if resultados_nao_operacionais else 0  # Soma dos valores absolutos das subcategorias

        # Construir subcategorias para Lucro Líquido com representatividade
        lucro_liquido_categorias = [
            {
                "subcategoria": r["categoria"],
                "valor": self.safe_float(r["valor"]),
                "av": round(self.safe_float(r["av"]), 2),
                "ah": round(self.safe_float(r["ah"]), 2),
                "representatividade": round(self.safe_float((abs(self.safe_float(r["valor"])) / lucro_liquido_subcategorias_total) * 100), 2)
                                     if lucro_liquido_subcategorias_total != 0 else 0
            } for r in lucro_liquido_resultado
        ]

        # Construir subcategorias para Entradas Não Operacionais com representatividade
        entradas_nao_operacionais_categorias = [
            {
                "subcategoria": e["categoria_nivel_3"],
                "valor": self.safe_float(e["total_valor"]),
                "av": round(self.safe_float(e["av"]), 2),
                "ah": round(self.safe_float(e["ah"]), 2),
                "representatividade": round(self.safe_float((abs(self.safe_float(e["total_valor"])) / entradas_nao_operacionais_subcategorias_total) * 100), 2)
                                     if entradas_nao_operacionais_subcategorias_total != 0 else 0
            } for e in entradas_nao_operacionais_resultado
        ]

        # Construir subcategorias para Resultados Não Operacionais com representatividade
        resultados_nao_operacionais_categorias = [
            {
                "subcategoria": r["nivel_1"],
                "valor": self.safe_float(r["total_valor"]),
                "av": round(self.safe_float(r["av"]), 2),
                "ah": round(self.safe_float(r["ah"]), 2),
                "representatividade": round(self.safe_float((abs(self.safe_float(r["total_valor"])) / resultados_nao_operacionais_subcategorias_total) * 100), 2)
                                    if resultados_nao_operacionais_subcategorias_total != 0 else 0
            } for r in resultados_nao_operacionais
        ]

        # Identificar a subcategoria mais representativa de Entradas Não Operacionais
        entradas_ordenadas = sorted(entradas_nao_operacionais_categorias, key=lambda x: x['representatividade'], reverse=True)
        primeira_cat_entradas = entradas_ordenadas[0]['subcategoria'] if entradas_ordenadas else "N/A"

        # Identificar a subcategoria mais representativa de Resultados Não Operacionais
        resultado_ordenado = sorted(resultados_nao_operacionais_categorias, key=lambda x: x['representatividade'], reverse=True)
        primeira_cat_resultado = resultado_ordenado[0]['subcategoria'] if resultado_ordenado else "N/A"

        # Calcular a análise horizontal (AH) para Lucro Líquido (média dos 'ah' das subcategorias)
        lucro_liquido_ah = round(sum(self.safe_float(r.get('ah', 0)) for r in lucro_liquido_resultado) / len(lucro_liquido_resultado), 2) if lucro_liquido_resultado else 0

        # Notas automatizadas
        notas_automatizadas = (
            f"Já o Lucro Líquido, dados os indicadores anteriores, fechou em R$ {lucro_liquido_atual:,.2f} "
            f"({av_lucro_liquido}% da Receita Total), uma variação de {lucro_liquido_ah}% em relação ao ano anterior. "
            f"As Entradas Não Operacionais fecharam com R$ {entradas_nao_operacionais_total:,.2f} "
            f"({round(self.safe_float(entradas_nao_operacionais_total / receita_atual * 100), 2) if receita_atual else 0}% da Receita Total), "
            f"com peso mais concentrado na categoria {primeira_cat_entradas}. "
            f"O Resultado Não Operacional fechou em R$ {resultados_nao_operacionais_total:,.2f} "
            f"({round(self.safe_float(resultados_nao_operacionais_total / receita_atual * 100), 2) if receita_atual else 0}% da Receita Total), "
            f"com peso mais concentrado na categoria {primeira_cat_resultado}."
        )

        # Verifica se não há dados relevantes (totais zero ou listas vazias)
        if (not lucro_liquido_resultado or lucro_liquido_atual == 0) and \
           (not entradas_nao_operacionais_resultado or entradas_nao_operacionais_total == 0) and \
           (not resultados_nao_operacionais or resultados_nao_operacionais_total == 0):
            notas_automatizadas = "Não há dados disponíveis para o período selecionado."

        return [
            {
                "categoria": "Lucro Líquido",
                "valor": lucro_liquido_atual,
                "subcategorias": lucro_liquido_categorias,
            },
            {
                "categoria": "Entradas Não Operacionais",
                "valor": entradas_nao_operacionais_total,
                "subcategorias": entradas_nao_operacionais_categorias,
            },
            
            {
                "categoria": "Resultados Não Operacionais",
                "valor": resultados_nao_operacionais_total,
                "subcategorias": resultados_nao_operacionais_categorias,
            }
        ], {
            "notas": notas_automatizadas
        }