# src/core/relatorios/relatorio_2.py
from datetime import date
from typing import Optional, List, Dict, Any
from src.core.indicadores import Indicadores

class Relatorio2:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> List[Dict[str, Any]]:
        """Gera o relatório 2 com lucro bruto, despesas fixas e suas representatividades.

        Args:
            mes_atual: Data do mês atual para o cálculo.
            mes_anterior: Data do mês anterior para análise horizontal (opcional).

        Returns:
            Lista de dicionários contendo categorias e subcategorias, junto com notas.
        """
        lucro_bruto = self.indicadores.calcular_lucro_bruto_fc(mes_atual)
        despesas_fixas = self.indicadores.calcular_despesas_fixas_fc(mes_atual)

        receita_total = next((r['valor'] for r in lucro_bruto if r['categoria'] == 'Receita'), 0)
        custos_total = next((r['valor'] for r in lucro_bruto if r['categoria'] == 'Custos Variáveis'), 0)
        lucro_bruto_total = receita_total - custos_total
        despesas_fixas_total = sum(abs(r['valor']) for r in despesas_fixas) if despesas_fixas else 0

        # Calcula a soma total das subcategorias de lucro bruto
        lucro_bruto_subcategorias_total = sum(r["valor"] for r in lucro_bruto[:3]) if lucro_bruto else 0
        # Calcula a soma total das subcategorias de despesas fixas
        despesas_fixas_subcategorias_total = sum(abs(d["valor"]) for d in despesas_fixas[:3]) if despesas_fixas else 0

        # Gera a lista de subcategorias de lucro bruto com representatividade
        lucro_bruto_categorias = [
            {
                "subcategoria": r["categoria"],
                "valor": r["valor"],
                "av": round(r["av"], 2) if r["av"] is not None else 0,
                "ah": round(r["ah"], 2) if r["ah"] is not None else 0,
                "representatividade": round((r["valor"] / lucro_bruto_subcategorias_total) * 100, 2) if lucro_bruto_subcategorias_total != 0 else 0
            } for r in lucro_bruto[:3]
        ]

        # Gera a lista de subcategorias de despesas fixas com representatividade
        despesas_fixas_categorias = [
            {
                "subcategoria": d["categoria"],
                "valor": abs(d["valor"]),
                "av": round(d["av"], 2) if d["av"] is not None else 0,
                "ah": round(d["ah"], 2) if d["ah"] is not None else 0,
                "representatividade": round((abs(d["valor"]) / despesas_fixas_subcategorias_total) * 100, 2) if despesas_fixas_subcategorias_total != 0 else 0
            } for d in despesas_fixas[:3]
        ]

        notas_automatizadas = (
            "O Lucro Bruto fechou o mês com um resultado de x% (R$ xx,xx) em relação à Receita Total, uma variação de x% em relação ao mês anterior. Quando olhamos para as Despesas Fixas, vemos um resultado de RS xx (x% da Receita Total), variação de x% em relação ao mês anterior, com destaque para (1ª categoria mais representativa).\n"
        )
        if not lucro_bruto and not despesas_fixas:
            notas_automatizadas = "Não há dados disponíveis para o período selecionado."

        return [
            {
                "categoria": "Lucro Bruto",
                "valor": lucro_bruto_total,
                "subcategorias": lucro_bruto_categorias,
            },
            {
                "categoria": "Despesas Fixas",
                "valor": despesas_fixas_total,
                "subcategorias": despesas_fixas_categorias,
            }
        ], {
            "notas": notas_automatizadas
        }