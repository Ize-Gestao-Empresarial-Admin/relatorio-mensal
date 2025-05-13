# src/core/relatorios/relatorio_4.py
from datetime import date
from typing import Optional, List, Dict, Any
from src.core.indicadores import Indicadores

class Relatorio4:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> List[Dict[str, Any]]:
        # Calcular mes_anterior se não fornecido
        if mes_anterior is None:
            mes_anterior = date(mes_atual.year if mes_atual.month > 1 else mes_atual.year - 1,
                                mes_atual.month - 1 if mes_atual.month > 1 else 12, 1)

        # Chamar funções de indicadores
        lucro_liquido_resultado = self.indicadores.calcular_lucro_liquido_fc(mes_atual)
        entradas_nao_operacionais_resultado = self.indicadores.calcular_entradas_nao_operacionais_fc(mes_atual)

        # Extrair valores do Lucro Líquido
        receita_atual = next((r['valor'] for r in lucro_liquido_resultado if r['categoria'] == 'Receita'), 0)
        custos_variaveis_atual = next((r['valor'] for r in lucro_liquido_resultado if r['categoria'] == 'Custos Variáveis'), 0)
        despesas_fixas_atual = next((r['valor'] for r in lucro_liquido_resultado if r['categoria'] == 'Despesas Fixas'), 0)
        investimentos_atual = next((r['valor'] for r in lucro_liquido_resultado if r['categoria'] == 'Investimentos'), 0)
        lucro_liquido_atual = receita_atual - custos_variaveis_atual - despesas_fixas_atual - investimentos_atual

        # Análise Vertical (AV) do Lucro Líquido
        av_lucro_liquido = round((lucro_liquido_atual / receita_atual) * 100, 2) if receita_atual else 0

        # Calcular soma total para representatividade (usar valores absolutos para evitar problemas com negativos)
        lucro_liquido_subcategorias_total = sum(abs(r["valor"]) for r in lucro_liquido_resultado) if lucro_liquido_resultado else 0
        entradas_nao_operacionais_subcategorias_total = sum(e["total_valor"] for e in entradas_nao_operacionais_resultado) if entradas_nao_operacionais_resultado else 0

        # Construir subcategorias para Lucro Líquido com representatividade
        lucro_liquido_categorias = [
            {
                "subcategoria": r["categoria"],
                "valor": r["valor"],
                "av": round(r["av"], 2) if r["av"] is not None else 0,
                "ah": round(r["ah"], 2) if r["ah"] is not None else 0,
                "representatividade": round((abs(r["valor"]) / lucro_liquido_subcategorias_total) * 100, 2) if lucro_liquido_subcategorias_total != 0 else 0
            } for r in lucro_liquido_resultado
        ]

        # Construir subcategorias para Entradas Não Operacionais com representatividade
        entradas_nao_operacionais_categorias = [
            {
                "subcategoria": e["categoria_nivel_3"],
                "valor": e["total_valor"],
                "av": round(e["av"], 2) if e["av"] is not None else 0,
                "ah": round(e["ah"], 2) if e["ah"] is not None else 0,
                "representatividade": round((e["total_valor"] / entradas_nao_operacionais_subcategorias_total) * 100, 2) if entradas_nao_operacionais_subcategorias_total != 0 else 0
            } for e in entradas_nao_operacionais_resultado
        ]

        # Identificar a subcategoria mais representativa de Entradas Não Operacionais
        entradas_ordenadas = sorted(entradas_nao_operacionais_categorias, key=lambda x: x['representatividade'], reverse=True)
        primeira_cat_entradas = entradas_ordenadas[0]['subcategoria'] if entradas_ordenadas else "N/A"

        # Calcular a análise horizontal (AH) para Lucro Líquido (média dos 'ah' das subcategorias)
        lucro_liquido_ah = round(sum(r.get('ah', 0) for r in lucro_liquido_resultado) / len(lucro_liquido_resultado), 2) if lucro_liquido_resultado else 0

        # Calcular o total de Entradas Não Operacionais
        entradas_nao_operacionais_total = sum(e["total_valor"] for e in entradas_nao_operacionais_resultado)

        # Notas automatizadas
        notas_automatizadas = (
            "Já o Lucro Líquido, dados os indicadores anteriores, fechou em R$ xx (x% da Receita Total), uma variação de x% em relação ao mês anterior. As entradas não operacionais fecharam com R$ xx (x% da Receita Total), com peso mais concentrado na categoria (1ª categoria mais representativa). \n"
        )

        # Mensagem padrão
        if (receita_atual == 0 and custos_variaveis_atual == 0 and 
            despesas_fixas_atual == 0 and investimentos_atual == 0 and 
            not entradas_nao_operacionais_resultado):
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
            }
        ], {
            "notas": notas_automatizadas
        }