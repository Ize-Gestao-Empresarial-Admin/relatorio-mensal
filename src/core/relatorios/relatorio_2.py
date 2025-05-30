# src/core/relatorios/relatorio_2.py
from datetime import date
from typing import Optional, List, Dict, Any
from src.core.indicadores import Indicadores
from dateutil.relativedelta import relativedelta
from src.core.utils import calcular_outras_categorias, safe_float

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
        # Calcula mês anterior automaticamente se não for passado
        if mes_anterior is None:
            mes_anterior = mes_atual - relativedelta(months=1)
        
        # Obtém dados do período atual
        lucro_bruto = self.indicadores.calcular_lucro_bruto_fc(mes_atual)
        despesas_fixas = self.indicadores.calcular_despesas_fixas_fc(mes_atual)
        lucro_bruto_anterior = self.indicadores.calcular_lucro_bruto_fc(mes_anterior)
        despesas_fixas_anterior = self.indicadores.calcular_despesas_fixas_fc(mes_anterior)

        # Calcula receita total e totais das categorias
        receita_total = next((r['valor'] for r in lucro_bruto if r['categoria'] == 'Receita'), 0)
        custos_total = next((r['valor'] for r in lucro_bruto if r['categoria'] == 'Custos Variáveis'), 0)
        lucro_bruto_total = receita_total - custos_total
        despesas_fixas_total = sum(abs(r['valor']) for r in despesas_fixas) if despesas_fixas else 0

        # Calcula totais do período anterior
        receita_total_anterior = next((r['valor'] for r in lucro_bruto_anterior if r['categoria'] == 'Receita'), 0)
        custos_total_anterior = next((r['valor'] for r in lucro_bruto_anterior if r['categoria'] == 'Custos Variáveis'), 0)
        lucro_bruto_anterior_total = receita_total_anterior - custos_total_anterior
        despesas_fixas_anterior_total = sum(abs(r['valor']) for r in despesas_fixas_anterior) if despesas_fixas_anterior else 0

        # Calcula subcategorias com "Outras categorias" para Lucro Bruto
        lucro_bruto_categorias = calcular_outras_categorias(
            items=lucro_bruto,
            items_anterior=lucro_bruto_anterior,
            total_atual=lucro_bruto_total,
            total_anterior=lucro_bruto_anterior_total,
            receita_total=receita_total,
            chave_valor="valor",
            chave_nome="categoria",
            top_n=3,
            usar_valor_abs=False
        )

        # Calcula subcategorias com "Outras categorias" para Despesas Fixas
        despesas_fixas_categorias = calcular_outras_categorias(
            items=despesas_fixas,
            items_anterior=despesas_fixas_anterior,
            total_atual=despesas_fixas_total,
            total_anterior=despesas_fixas_anterior_total,
            receita_total=receita_total,
            chave_valor="valor",
            chave_nome="categoria",
            top_n=3,
            usar_valor_abs=True
        )

        # Calcula AV para lucro bruto (em relação à receita total)
        lucro_bruto_av = round((lucro_bruto_total / receita_total * 100) if receita_total != 0 else 0, 2)

        # Calcula AV para despesas fixas (em relação à receita total)
        despesas_fixas_av = round((despesas_fixas_total / receita_total * 100) if receita_total != 0 else 0, 2)

        # Calcula AH para lucro bruto
        lucro_bruto_variacao = round(
            ((lucro_bruto_total / lucro_bruto_anterior_total - 1) * 100) if lucro_bruto_anterior_total != 0 else 0, 2
        )

        # Calcula AH para despesas fixas
        despesas_fixas_variacao = round(
            ((despesas_fixas_total / despesas_fixas_anterior_total - 1) * 100) if despesas_fixas_anterior_total != 0 else 0, 2
        )

        # Identifica a categoria de maior peso para despesas fixas
        categoria_maior_peso_despesas = max(
            despesas_fixas_categorias, key=lambda x: x['representatividade'], default={'subcategoria': 'N/A'}
        )['subcategoria']

        # Formata a nota automatizada
        notas_automatizadas = (
            f"O Lucro Bruto fechou o mês com um resultado de {lucro_bruto_av}% "
            f"(R$ {lucro_bruto_total:,.2f}) em relação à Receita Total, "
            f"uma variação de {lucro_bruto_variacao}% em relação ao mês anterior. "
            f"Quando olhamos para as Despesas Fixas, vemos um resultado de R$ {despesas_fixas_total:,.2f} "
            f"({despesas_fixas_av}% da Receita Total), variação de {despesas_fixas_variacao}% "
            f"em relação ao mês anterior, com destaque para {categoria_maior_peso_despesas}."
        )

        # Verifica se há dados válidos
        if (not lucro_bruto or all(safe_float(r.get("valor", 0)) == 0 for r in lucro_bruto)) and \
           (not despesas_fixas or all(safe_float(d.get("valor", 0)) == 0 for d in despesas_fixas)):
            notas_automatizadas = "Não há dados disponíveis para o período selecionado."

        return [
            {
                "categoria": "Lucro Bruto",
                "valor": lucro_bruto_total,
                "av_categoria": lucro_bruto_av,
                "subcategorias": lucro_bruto_categorias,
            },
            {
                "categoria": "Despesas Fixas",
                "valor": -despesas_fixas_total,  # Despesas são negativas
                "av_categoria": despesas_fixas_av,
                "subcategorias": despesas_fixas_categorias,
            }
        ], {
            "notas": notas_automatizadas
        }