#src/core/relatorios/relatorio_.py
from datetime import date
from typing import Optional, List, Dict, Any
from src.core.indicadores import Indicadores

class Relatorio3:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> List[Dict[str, Any]]:
        # Calcular mes_anterior se não fornecido
        if mes_anterior is None:
            mes_anterior = date(mes_atual.year if mes_atual.month > 1 else mes_atual.year - 1,
                                mes_atual.month - 1 if mes_atual.month > 1 else 12, 1)

        # Chamar funções de indicadores
        lucro_operacional_resultado = self.indicadores.calcular_lucro_operacional_fc(mes_atual, mes_anterior)
        investimentos_resultado = self.indicadores.calcular_investimentos_fc(mes_atual, mes_anterior)

        # Extrair valores, tratando None explicitamente
        def get_valor(categoria: str, resultado: List[Dict[str, Any]], default: float = 0.0) -> float:
            valor = next((r['valor'] for r in resultado if r['categoria'] == categoria), default)
            return valor if valor is not None else default

        receita_atual = get_valor('Receita', lucro_operacional_resultado)
        custos_variaveis_atual = get_valor('Custos Variáveis', lucro_operacional_resultado)
        despesas_fixas_atual = get_valor('Despesas Fixas', lucro_operacional_resultado)
        lucro_operacional_atual = receita_atual - custos_variaveis_atual - despesas_fixas_atual
        investimentos_atual = sum(r['valor'] if r['valor'] is not None else 0 for r in investimentos_resultado)


        # Calcular a soma total das subcategorias de Lucro Operacional
        lucro_operacional_subcategorias_total = sum(abs(r["valor"]) if r["valor"] is not None else 0 for r in lucro_operacional_resultado) if lucro_operacional_resultado else 0
        # Calcular a soma total das subcategorias de Investimentos
        investimentos_subcategorias_total = sum(abs(r["valor"]) if r["valor"] is not None else 0 for r in investimentos_resultado) if investimentos_resultado else 0

        # Construir subcategorias para Lucro Operacional com representatividade
        lucro_operacional_categorias = [
            {
                "subcategoria": r["categoria"],
                "valor": r["valor"] if r["valor"] is not None else 0,
                "av": round(r["av"], 2) if r["av"] is not None else 0,
                "ah": round(r["ah"], 2) if r["ah"] is not None else 0,
                "representatividade": round(abs(r["valor"]) / lucro_operacional_subcategorias_total * 100, 2)
                if lucro_operacional_subcategorias_total != 0 and r["valor"] is not None else 0
            } for r in lucro_operacional_resultado [:3]
        ]

        # Construir subcategorias para Investimentos, ordenadas do maior para o menor (em valor absoluto), limitando a 3
        investimentos_categorias = [
            {
                "subcategoria": i["categoria"],
                "valor": i["valor"] if i["valor"] is not None else 0,
                "av": round(i["av"], 2) if i["av"] is not None else 0,
                "ah": round(i["ah"], 2) if i["ah"] is not None else 0,
                "representatividade": round(abs(i["valor"]) / investimentos_subcategorias_total * 100, 2)
                if investimentos_subcategorias_total != 0 and i["valor"] is not None else 0
            } for i in sorted(investimentos_resultado, key=lambda x: abs(x["valor"] if x["valor"] is not None else 0), reverse=True)[:3]
        ]

        ####### SEÇÃO NOTAS AUTOMATIZADAS ########

        # Calcula valores do mês anterior para análise horizontal (AH)
        lucro_operacional_anterior = 0
        investimentos_anterior = 0
        if mes_anterior:
            lucro_operacional_anterior_resultado = self.indicadores.calcular_lucro_operacional_fc(mes_anterior, None)
            investimentos_anterior_resultado = self.indicadores.calcular_investimentos_fc(mes_anterior, None)
            
            receita_anterior = get_valor('Receita', lucro_operacional_anterior_resultado)
            custos_variaveis_anterior = get_valor('Custos Variáveis', lucro_operacional_anterior_resultado)
            despesas_fixas_anterior = get_valor('Despesas Fixas', lucro_operacional_anterior_resultado)
            lucro_operacional_anterior = receita_anterior - custos_variaveis_anterior - despesas_fixas_anterior
            investimentos_anterior = sum(abs(r['valor']) if r['valor'] is not None else 0 for r in investimentos_anterior_resultado) if investimentos_anterior_resultado else 0

        # Calcula AV para lucro operacional
        lucro_operacional_av = round((lucro_operacional_atual / receita_atual * 100) if receita_atual != 0 else 0, 2)
        #round((despesas_fixas_total / receita_total * 100) if receita_total != 0 else 0, 2)

        # Calcula AH para lucro operacional
        lucro_operacional_ah = round(((lucro_operacional_atual / lucro_operacional_anterior - 1) * 100) if lucro_operacional_anterior != 0 else 0, 2)

        # Calcula AH para investimentos
        investimentos_ah = round(((investimentos_atual / investimentos_anterior - 1) * 100) if investimentos_anterior != 0 else 0, 3)
        investimentos_av = round((investimentos_atual / receita_atual * 100) if receita_atual != 0 else 0, 2)

        # Obtém a categoria mais representativa dos investimentos
        categoria_maior_peso_investimentos_1 = investimentos_categorias[0]["subcategoria"] if investimentos_categorias else "N/A"

        # Monta o dicionário com os valores calculados
        notas_automatizadas_valores = {
            "lucro_operacional": lucro_operacional_atual,
            "lucro_operacional_av": lucro_operacional_av,
            "lucro_operacional_ah": lucro_operacional_ah,
            "investimentos": investimentos_atual,
            "investimentos_ah": investimentos_ah,
            'investimentos_av': investimentos_av,
            "categoria_maior_peso_investimentos_1": categoria_maior_peso_investimentos_1,
        }

        # Formata a nota automatizada com os valores calculados
        notas_automatizadas = (
            f"O nosso principal indicador de eficiência da empresa, o Lucro Operacional, fechou em {lucro_operacional_av}% "
            f"(R$ {lucro_operacional_atual:,.2f}) em relação à Receita Total, "
            f"uma variação de {lucro_operacional_ah}% em relação ao mês anterior. "
            f"Nos investimentos, totalizamos R$ {investimentos_atual:,.2f}, {investimentos_ah}% em relação ao mês anterior, "
            f"com protagonismo da categoria {categoria_maior_peso_investimentos_1}."
        )

        # Verifica se não há dados relevantes (listas vazias ou totais zero)
        if (not lucro_operacional_resultado or lucro_operacional_atual == 0) and \
        (not investimentos_resultado or investimentos_atual == 0):
            notas_automatizadas = "Não há dados disponíveis para o período selecionado."

        return [
            {
                "categoria": "Lucro Operacional",
                "valor": lucro_operacional_atual,
                "av_categoria": lucro_operacional_av,
                "subcategorias": lucro_operacional_categorias,
            },
            {
                "categoria": "Investimentos",
                "valor": investimentos_atual,
                "av_categoria": investimentos_av,
                "subcategorias": investimentos_categorias,
            }
        ], {
            "notas": notas_automatizadas
        }