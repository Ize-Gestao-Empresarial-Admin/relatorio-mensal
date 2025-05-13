from datetime import date
from typing import Optional, List, Dict, Any
from src.core.indicadores import Indicadores

class Relatorio3:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> List[Dict[str, Any]]:
        # Calcular mes_anterior se não fornecido, como na lógica antiga
        if mes_anterior is None:
            mes_anterior = date(mes_atual.year if mes_atual.month > 1 else mes_atual.year - 1,
                                mes_atual.month - 1 if mes_atual.month > 1 else 12, 1)

        # Chamar funções de indicadores
        lucro_operacional_resultado = self.indicadores.calcular_lucro_operacional_fc(mes_atual, mes_anterior)
        investimentos_resultado = self.indicadores.calcular_investimentos_fc(mes_atual, mes_anterior)

        # Extrair valores, como na lógica antiga
        receita_atual = next((r['valor'] for r in lucro_operacional_resultado if r['categoria'] == 'Receita'), 0)
        custos_variaveis_atual = next((r['valor'] for r in lucro_operacional_resultado if r['categoria'] == 'Custos Variáveis'), 0)
        despesas_fixas_atual = next((r['valor'] for r in lucro_operacional_resultado if r['categoria'] == 'Despesas Fixas'), 0)
        lucro_operacional_atual = receita_atual - custos_variaveis_atual - despesas_fixas_atual
        investimentos_atual = sum(r['valor'] for r in investimentos_resultado) if investimentos_resultado else 0

        # Calcular a soma total das subcategorias de Lucro Operacional
        lucro_operacional_subcategorias_total = sum(abs(r["valor"]) for r in lucro_operacional_resultado) if lucro_operacional_resultado else 0
        # Calcular a soma total das subcategorias de Investimentos
        investimentos_subcategorias_total = sum(abs(r["valor"]) for r in investimentos_resultado[:3]) if investimentos_resultado else 0

        # Construir subcategorias para Lucro Operacional com representatividade
        lucro_operacional_categorias = [
            {
                "subcategoria": r["categoria"],
                "valor": r["valor"],
                "av": round(r["av"], 2) if r["av"] is not None else 0,
                "ah": round(r["ah"], 2) if r["ah"] is not None else 0,
                "representatividade": round((abs(r["valor"]) / lucro_operacional_subcategorias_total) * 100, 2)
                if lucro_operacional_subcategorias_total != 0 else 0
            } for r in lucro_operacional_resultado
        ]

        # Construir subcategorias para Investimentos, ordenadas do maior para o menor (em valor absoluto), limitando a 3
        investimentos_categorias = [
            {
                "subcategoria": i["categoria"],
                "valor": i["valor"],  # Manter valores negativos, como na antiga
                "av": round(i["av"], 2) if i["av"] is not None else 0,
                "ah": round(i["ah"], 2) if i["ah"] is not None else 0,
                "representatividade": round((abs(i["valor"]) / investimentos_subcategorias_total) * 100, 2)
                if investimentos_subcategorias_total != 0 else 0
            } for i in sorted(investimentos_resultado, key=lambda x: abs(x["valor"]), reverse=True)[:3]
        ]

        # Notas automatizadas, adaptadas da lógica antiga
        categorias_lucro_operacional = [
            {"categoria": "Receita", "av": next((r['av'] for r in lucro_operacional_resultado if r['categoria'] == 'Receita'), 0)},
            {"categoria": "Custos Variáveis", "av": next((r['av'] for r in lucro_operacional_resultado if r['categoria'] == 'Custos Variáveis'), 0)},
            {"categoria": "Despesas Fixas", "av": next((r['av'] for r in lucro_operacional_resultado if r['categoria'] == 'Despesas Fixas'), 0)}
        ]
        notas_automatizadas = (
            "O nosso principal indicador de eficiência da empresa, o Lucro Operacional, fechou em x% (R$ xx,xx) em relação à Receita Total, uma variação de x% em relação ao mês anterior. Nos investimento, totalizamos R$ xx, x% em relação ao mês anterior, com protagonismo da categoria (1ª categoria mais representativa).\n"
        )

        # Mensagem padrão, como na lógica antiga
        if lucro_operacional_atual == 0 and investimentos_atual == 0:
            notas_automatizadas = "Não há dados disponíveis para o período selecionado."

        return [
            {
                "categoria": "Lucro Operacional",
                "valor": lucro_operacional_atual,
                "subcategorias": lucro_operacional_categorias,
            },
            {
                "categoria": "Investimentos",
                "valor": investimentos_atual,  # Manter valor negativo, como na antiga
                "subcategorias": investimentos_categorias,
            }
        ], {
            "notas": notas_automatizadas
        }