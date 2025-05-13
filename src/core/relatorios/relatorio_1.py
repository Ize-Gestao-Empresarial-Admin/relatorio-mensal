# src/core/relatorios/relatorio_1.py
from datetime import date
from typing import Optional, List, Dict, Any
from src.core.indicadores import Indicadores

class Relatorio1:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        """Inicializa a classe Relatorio1 com indicadores e nome do cliente.

        Args:
            indicadores: Instância da classe Indicadores.
            nome_cliente: Nome do cliente associado ao relatório.
        """
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> List[Dict[str, Any]]:
        """Gera o relatório 1 com receitas, custos variáveis e suas representatividades.

        Args:
            mes_atual: Data do mês atual para o cálculo.
            mes_anterior: Data do mês anterior para análise horizontal (opcional).

        Returns:
            Lista de dicionários contendo categorias e subcategorias, junto com notas.
        """
        lucro_operacional = self.indicadores.calcular_lucro_operacional_fc(mes_atual, mes_anterior)
        receitas = self.indicadores.calcular_receitas_fc(mes_atual, '3.%')
        custos = self.indicadores.calcular_custos_variaveis_fc(mes_atual, '4.%')

        receita_total = next((r['valor'] for r in lucro_operacional if r['categoria'] == 'Receita'), 0)
        custos_total = next((r['valor'] for r in lucro_operacional if r['categoria'] == 'Custos Variáveis'), 0)

        # Calcula a soma total das subcategorias de receitas
        receita_subcategorias_total = sum(r["total_categoria"] for r in receitas[:3]) if receitas else 0
        # Calcula a soma total das subcategorias de custos
        custos_subcategorias_total = sum(c["total_categoria"] for c in custos[:3]) if custos else 0

        # Gera a lista de subcategorias de receitas com representatividade
        receitas_categoria = [
            {
                "subcategoria": r["categoria_nivel_3"],
                "valor": r["total_categoria"],
                "av": round(r["av"], 2) if r["av"] is not None else 0,
                "ah": round(r["ah"], 2) if r["ah"] is not None else 0,
                "representatividade": round((r["total_categoria"] / receita_subcategorias_total) * 100, 2) if receita_subcategorias_total != 0 else 0
            } for r in receitas[:3]
        ]

        # Gera a lista de subcategorias de custos variáveis com representatividade
        custos_variaveis = [
            {
                "subcategoria": c["nivel_2"],
                "valor": c["total_categoria"],
                "av": round(c["av"], 2) if c["av"] is not None else 0,
                "ah": round(c["ah"], 2) if c["ah"] is not None else 0,
                "representatividade": round((c["total_categoria"] / custos_subcategorias_total) * 100, 2) if custos_subcategorias_total != 0 else 0
            } for c in custos[:3]  # limita para 3 categorias
        ]

        # Obtém informação da receita para análise horizontal
        receita_ah = next((r['ah'] for r in lucro_operacional if r['categoria'] == 'Receita'), 0)
        
        # Identifica as categorias mais representativas das receitas (ordenadas por representatividade)
        receitas_ordenadas = sorted(receitas_categoria, key=lambda x: x['representatividade'], reverse=True)
        primeira_cat_receita = receitas_ordenadas[0]['subcategoria'] if len(receitas_ordenadas) > 0 else "N/A"
        segunda_cat_receita = receitas_ordenadas[1]['subcategoria'] if len(receitas_ordenadas) > 1 else "N/A"
        
        # Identifica a categoria mais representativa dos custos
        custos_ordenados = sorted(custos_variaveis, key=lambda x: x['representatividade'], reverse=True)
        primeira_cat_custo = custos_ordenados[0]['subcategoria'] if len(custos_ordenados) > 0 else "N/A"
        
        notas_automatizadas = (
            f"No mês, observamos uma receita operacional de R${receita_total:,.2f}, "
            f"uma variação de {receita_ah:.2f}% em relação ao mês anterior, "
            f"com principal peso na categoria {primeira_cat_receita} e {segunda_cat_receita}. "
            f"Em relação aos custos variáveis, tivemos um resultados de R${custos_total:,.2f}, "
            f"com destaque para {primeira_cat_custo}."
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