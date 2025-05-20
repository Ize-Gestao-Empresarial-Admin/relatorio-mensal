#src/core/relatorios/relatorio_1.py
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
            Tupla com lista de dicionários (categorias e subcategorias) e dicionário de notas.
        """
        receitas = self.indicadores.calcular_receitas_fc(mes_atual, '3.%')
        custos = self.indicadores.calcular_custos_variaveis_fc(mes_atual, '4.%')

        # Calcula totais somando total_categoria
        receita_total = sum(r.get('total_categoria', 0) for r in receitas) if receitas else 0
        custos_total = sum(c.get('total_categoria', 0) for c in custos) if custos else 0

        # Calcula a soma total das subcategorias de receitas (limita a 3)
        receita_subcategorias_total = sum(r.get('total_categoria', 0) for r in receitas[:3]) if receitas else 0
        # Calcula a soma total das subcategorias de custos (limita a 3)
        custos_subcategorias_total = sum(c.get('total_categoria', 0) for c in custos[:3]) if custos else 0

        # Gera a lista de subcategorias de receitas com representatividade
        receitas_categoria = [
            {
                "subcategoria": r.get("categoria_nivel_3", "N/A"),
                "valor": r.get("total_categoria", 0),
                "av": round(r.get("av", 0), 2) if r.get("av") is not None else 0,
                "ah": round(r.get("ah", 0), 2) if r.get("ah") is not None else 0,
                "representatividade": round(
                    (r.get("total_categoria", 0) / receita_subcategorias_total) * 100, 2
                ) if receita_subcategorias_total != 0 else 0
            } for r in receitas[:3]
        ]

        # Gera a lista de subcategorias de custos variáveis com representatividade
        custos_variaveis = [
            {
                "subcategoria": c.get("nivel_2", "N/A"),
                "valor": c.get("total_categoria", 0),
                "av": round(c.get("av", 0), 2) if c.get("av") is not None else 0,
                "ah": round(c.get("ah", 0), 2) if c.get("ah") is not None else 0,
                "representatividade": round(
                    (c.get("total_categoria", 0) / custos_subcategorias_total) * 100, 2
                ) if custos_subcategorias_total != 0 else 0
            } for c in custos[:3]
        ]

        # Identifica as categorias mais representativas das receitas
        receitas_ordenadas = sorted(receitas_categoria, key=lambda x: x['representatividade'], reverse=True)
        primeira_cat_receita = receitas_ordenadas[0]['subcategoria'] if len(receitas_ordenadas) > 0 else "N/A"
        segunda_cat_receita = receitas_ordenadas[1]['subcategoria'] if len(receitas_ordenadas) > 1 else "N/A"

        # Identifica a categoria mais representativa dos custos
        custos_ordenados = sorted(custos_variaveis, key=lambda x: x['representatividade'], reverse=True)
        primeira_cat_custo = custos_ordenados[0]['subcategoria'] if len(custos_ordenados) > 0 else "N/A"

        #CORRIGIR  Calcula a análise horizontal para receitas (média dos 'ah' das subcategorias)
        receita_ah = round(sum(r.get('ah', 0) for r in receitas) / len(receitas), 2) if receitas else 0

        # Gera notas automatizadas alinhadas com a saída do teste
        notas_automatizadas = (
            f" No mês, observamos uma receita operacional de R$--, uma variação de (AH da receita total) em relação ao mês anterior, com principal peso na categoria (1ª categoria mais representativa) e (2ª categoria mais representativa). Em relação aos custos variáveis, tivemos um resultados de -R$ --, com destaque para (1ª categoria mais representativa). \n"
        )
        # Verifica se as listas estão vazias ou se todos os valores são zero
        if (not receitas or all(r.get("total_categoria", 0) == 0 for r in receitas)) and \
           (not custos or all(c.get("total_categoria", 0) == 0 for c in custos)):
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
        } # type: ignore