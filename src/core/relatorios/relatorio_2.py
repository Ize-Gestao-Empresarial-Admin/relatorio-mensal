#src/core/relatorios/relatorio_2.py
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
        lucro_bruto_subcategorias_total = sum(r["valor"] for r in lucro_bruto) if lucro_bruto else 0
        # Calcula a soma total das subcategorias de despesas fixas
        despesas_fixas_subcategorias_total = sum(abs(d["valor"]) for d in despesas_fixas) if despesas_fixas else 0

        # Gera a lista de subcategorias de lucro bruto com representatividade
        lucro_bruto_categorias = [
            {
                "subcategoria": r["categoria"],
                "valor": r["valor"],
                "av": round(r["av"], 2) if r["av"] is not None else 0,
                "ah": round(r["ah"], 2) if r["ah"] is not None else 0,
                "representatividade": round(abs(r["valor"] / lucro_bruto_subcategorias_total) * 100, 2) if lucro_bruto_subcategorias_total != 0 else 0
            } for r in lucro_bruto[:3]
        ]

        # Gera a lista de subcategorias de despesas fixas com representatividade
        despesas_fixas_categorias = [
            {
                "subcategoria": d["categoria"],
                "valor": d["valor"],
                "av": round(d["av"], 2) if d["av"] is not None else 0,
                "ah": round(d["ah"], 2) if d["ah"] is not None else 0,
                "representatividade": round((abs(d["valor"]) / despesas_fixas_subcategorias_total) * 100, 2) if despesas_fixas_subcategorias_total != 0 else 0
            } for d in despesas_fixas[:3]
        ]

        
        ####### SEÇÃO DA NOTA AUTOMATICA E RETORNO DE VALORES ########

        # Calcula AV para lucro bruto (em relação à receita total)
        lucro_bruto_av = round((lucro_bruto_total / receita_total * 100) if receita_total != 0 else 0, 2)

        # Calcula AV para despesas fixas (em relação à receita total)
        despesas_fixas_av = round((despesas_fixas_total / receita_total * 100) if receita_total != 0 else 0, 2)

        # Calcula valores do mês anterior para análise horizontal (AH)
        lucro_bruto_anterior = 0
        despesas_fixas_anterior = 0
        if mes_anterior:
            lucro_bruto_anterior_data = self.indicadores.calcular_lucro_bruto_fc(mes_anterior)
            despesas_fixas_anterior_data = self.indicadores.calcular_despesas_fixas_fc(mes_anterior)
            
            receita_total_anterior = next((r['valor'] for r in lucro_bruto_anterior_data if r['categoria'] == 'Receita'), 0)
            custos_total_anterior = next((r['valor'] for r in lucro_bruto_anterior_data if r['categoria'] == 'Custos Variáveis'), 0)
            lucro_bruto_anterior = receita_total_anterior - custos_total_anterior
            despesas_fixas_anterior = sum(abs(r['valor']) for r in despesas_fixas_anterior_data) if despesas_fixas_anterior_data else 0

        # Calcula AH para lucro bruto
        lucro_bruto_variacao = round(((lucro_bruto_total / lucro_bruto_anterior - 1) * 100) if lucro_bruto_anterior != 0 else 0, 2)

        # Calcula AH para despesas fixas
        despesas_fixas_variacao = round(((despesas_fixas_total / despesas_fixas_anterior - 1) * 100) if despesas_fixas_anterior != 0 else 0, 2)

        # Monta o dicionário com os valores calculados
        notas_automatizadas_valores = {
            "lucro_bruto": lucro_bruto_total,
            "lucro_bruto_av": lucro_bruto_av,
            "lucro_bruto_variacao": lucro_bruto_variacao,
            "despesas_fixas": despesas_fixas_total,
            "despesas_fixas_av": despesas_fixas_av,
            "despesas_fixas_variacao": despesas_fixas_variacao,
            "categoria_maior_peso_despesas_1": despesas_fixas_categorias[0]["subcategoria"] if despesas_fixas_categorias else "",
        }

        # Formata a nota automatizada com os valores calculados
        notas_automatizadas = (
            f"O Lucro Bruto fechou o mês com um resultado de {lucro_bruto_av}% "
            f"(R$ {lucro_bruto_total:,.2f}) em relação à Receita Total, "
            f"uma variação de {lucro_bruto_variacao}% em relação ao mês anterior. "
            f"Quando olhamos para as Despesas Fixas, vemos um resultado de R$ {despesas_fixas_total:,.2f} "
            f"({despesas_fixas_av}% da Receita Total), variação de {despesas_fixas_variacao}% "
            f"em relação ao mês anterior, com destaque para {notas_automatizadas_valores['categoria_maior_peso_despesas_1']}."
        )

        # Verifica se as listas estão vazias ou se todos os valores são zero
        if (not lucro_bruto or all(r.get("valor", 0) == 0 for r in lucro_bruto)) and \
        (not despesas_fixas or all(d.get("valor", 0) == 0 for d in despesas_fixas)):
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
                "valor": despesas_fixas_total,
                "av_categoria": despesas_fixas_av,
                "subcategorias": despesas_fixas_categorias,
            }
        ], {
            "notas": notas_automatizadas
        }