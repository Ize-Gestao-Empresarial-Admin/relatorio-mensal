# src/core/relatorios/relatorio_1.py
from datetime import date
from typing import Optional, List, Dict, Any
from src.core.indicadores import Indicadores

class Relatorio1:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> List[Dict[str, Any]]:
        lucro_operacional = self.indicadores.calcular_lucro_operacional_fc(mes_atual, mes_anterior)
        receitas = self.indicadores.calcular_receitas_fc(mes_atual, '3.%')
        custos = self.indicadores.calcular_custos_variaveis_fc(mes_atual, '4.%')

        receita_total = next((r['valor'] for r in lucro_operacional if r['categoria'] == 'Receita'), 0)
        custos_total = next((r['valor'] for r in lucro_operacional if r['categoria'] == 'Custos Variáveis'), 0)

        receitas_categoria = [
            {
                "subcategoria": r["categoria_nivel_3"],
                "valor": r["total_categoria"],
                "av": round(r["av"], 2) if r["av"] is not None else 0,
                "ah": round(r["ah"], 2) if r["ah"] is not None else 0
            } for r in receitas[:3]
        ]

        custos_variaveis = [
            {
                "subcategoria": c["nivel_2"],
                "valor": c["total_categoria"],
                "av": round(c["av"], 2) if c["av"] is not None else 0,
                "ah": round(c["ah"], 2) if c["ah"] is not None else 0
            } for c in custos[:3] # limita para 3 categorias
        ]

        notas_automatizadas = (
            "Os custos variáveis são gastos diretamente associados à operação da empresa, "
            f"como matéria-prima, comissões de vendas e custos de produção. "
            f"Destaques: Receita Total={receita_total}, Custos Variáveis Total={custos_total}."
        )
        if not receitas and not custos:
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