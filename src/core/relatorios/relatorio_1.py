#src/core/relatorios/relatorio_1.py
from datetime import date
from typing import Optional, List, Dict, Any
from src.core.indicadores import Indicadores
import math  # Importado para verificar NaN

class Relatorio1:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        """Inicializa a classe Relatorio1 com indicadores e nome do cliente.

        Args:
            indicadores: Instância da classe Indicadores.
            nome_cliente: Nome do cliente associado ao relatório.
        """
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

        # Calcula a soma total das subcategorias de receitas
        receita_subcategorias_total = sum(r.get('total_categoria', 0) for r in receitas) if receitas else 0
        # Calcula a soma total das subcategorias de custos
        custos_subcategorias_total = sum(c.get('total_categoria', 0) for c in custos) if custos else 0

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
                )if custos_subcategorias_total != 0 else 0
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

        ####### SECAO NOTAS AUTOMATIZADAS ########

        # Calcula a receita total do mês anterior para análise horizontal (AH)
        receita_total_mes_anterior = 0
        receita_total_anterior = 0
        if mes_anterior:
            receitas_anterior = self.indicadores.calcular_receitas_fc(mes_anterior, '3.%')
            receita_total_anterior = sum(r.get('total_categoria', 0) for r in receitas_anterior) if receitas_anterior else 0

        # Calcula AH para receita total
        receita_total_ah = round(((receita_total / receita_total_anterior - 1) * 100) if receita_total_anterior != 0 else 0, 2)

        # Monta o dicionário com os valores calculados
        notas_automatizadas_valores = {
            "receita_total": receita_total,
            "receita_total_ah": receita_total_ah,
            "categoria_maior_peso_receitas_1": primeira_cat_receita,
            "categoria_maior_peso_receitas_2": segunda_cat_receita,
            "custos_variaveis_total": custos_total,
            "categoria_maior_peso_custos_1": primeira_cat_custo,
        }

        # Formata a nota automatizada com os valores calculados
        notas_automatizadas = (
            f"No mês, observamos uma receita operacional de R$ {receita_total:,.2f}, "
            f"uma variação de {receita_total_ah}% em relação ao mês anterior, "
            f"com principal peso na categoria {primeira_cat_receita} e {segunda_cat_receita}. "
            f"Em relação aos custos variáveis, tivemos um resultado de R$ {custos_total:,.2f}, "
            f"com destaque para {primeira_cat_custo}."
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