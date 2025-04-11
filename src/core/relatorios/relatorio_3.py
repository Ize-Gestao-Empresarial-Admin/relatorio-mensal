# src/core/relatorios/relatorio_3.py
from datetime import date, timedelta
from typing import Optional
from src.core.indicadores import Indicadores
from src.core.analises import AnalisesFinanceiras

class Relatorio3:
    CATEGORIAS_RECEITA = ["3. Receitas"]
    CATEGORIAS_CUSTOS_VARIAVEIS = ["4. Custos Variáveis"]
    CATEGORIAS_DESPESAS_FIXAS = ["5. Despesas Fixas"]
    CATEGORIAS_INVESTIMENTOS = ["6. Investimentos"]
    CATEGORIAS_ENTRADAS_NAO_OPERACIONAIS = ["7.1 Entradas Não Operacionais", "7.1 Entradas não operacionais"]
    CATEGORIAS_SAIDAS_NAO_OPERACIONAIS = ["7.2 Saídas Não Operacionais", "7.2 Saídas não operacionais"]

    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def _calcular_dados_meses(self, mes_atual: date, meses: int = 3) -> dict:
        """Calcula dados para os últimos 'meses' fechados antes do mês atual."""
        dados = {"Receita": [], "Custos Variáveis": [], "Despesas Fixas": [], "Investimentos": [],
                 "Entradas Não Operacionais": [], "Saídas Não Operacionais": [], "Lucro Operacional": []}
        for i in range(1, meses + 1):
            mes = (mes_atual - timedelta(days=31 * i)).replace(day=1)
            receita = self.indicadores.calcular_nivel_lucros(mes, self.CATEGORIAS_RECEITA)
            custos_variaveis = self.indicadores.calcular_nivel_lucros(mes, self.CATEGORIAS_CUSTOS_VARIAVEIS)
            despesas_fixas = self.indicadores.calcular_nivel_lucros(mes, self.CATEGORIAS_DESPESAS_FIXAS)
            investimentos = self.indicadores.calcular_nivel_lucros(mes, self.CATEGORIAS_INVESTIMENTOS)
            entradas_nao_oper = self.indicadores.calcular_nivel_lucros(mes, self.CATEGORIAS_ENTRADAS_NAO_OPERACIONAIS)
            saidas_nao_oper = self.indicadores.calcular_nivel_lucros(mes, self.CATEGORIAS_SAIDAS_NAO_OPERACIONAIS)
            lucro_operacional = receita + custos_variaveis + despesas_fixas

            dados["Receita"].append(receita)
            dados["Custos Variáveis"].append(custos_variaveis)
            dados["Despesas Fixas"].append(despesas_fixas)
            dados["Investimentos"].append(investimentos)
            dados["Entradas Não Operacionais"].append(entradas_nao_oper)
            dados["Saídas Não Operacionais"].append(saidas_nao_oper)
            dados["Lucro Operacional"].append(lucro_operacional)
        return dados

    def _calcular_ponto_equilibrio(self, dados_3_meses: dict, lucro_operacional_atual: float) -> float:
        """Calcula o Ponto de Equilíbrio com base na média dos últimos 3 meses fechados."""
        despesa_fixa_media = sum(dados_3_meses["Despesas Fixas"]) / 3
        receita_media = sum(dados_3_meses["Receita"]) / 3
        custo_variavel_media = sum(dados_3_meses["Custos Variáveis"]) / 3

        av_custo_variavel = (custo_variavel_media / receita_media) if receita_media else 0
        margem_contribuicao = 1 - av_custo_variavel

        ponto_equilibrio = despesa_fixa_media / margem_contribuicao if margem_contribuicao else 0
        if lucro_operacional_atual > 0:
            ponto_equilibrio -= lucro_operacional_atual
        return ponto_equilibrio

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> dict:
        """Gera o relatório financeiro 3 - Análise de Lucros."""
        # Dados dos últimos 3 meses fechados
        dados_3_meses = self._calcular_dados_meses(mes_atual)

        # Cálculos do mês atual
        receita = self.indicadores.calcular_nivel_lucros(mes_atual, self.CATEGORIAS_RECEITA)
        custos_variaveis = self.indicadores.calcular_nivel_lucros(mes_atual, self.CATEGORIAS_CUSTOS_VARIAVEIS)
        despesas_fixas = self.indicadores.calcular_nivel_lucros(mes_atual, self.CATEGORIAS_DESPESAS_FIXAS)
        investimentos = self.indicadores.calcular_nivel_lucros(mes_atual, self.CATEGORIAS_INVESTIMENTOS)
        entradas_nao_operacionais = self.indicadores.calcular_nivel_lucros(mes_atual, self.CATEGORIAS_ENTRADAS_NAO_OPERACIONAIS)
        saidas_nao_operacionais = self.indicadores.calcular_nivel_lucros(mes_atual, self.CATEGORIAS_SAIDAS_NAO_OPERACIONAIS)

        # Indicadores principais
        lucro_bruto = receita + custos_variaveis
        lucro_operacional = lucro_bruto + despesas_fixas
        lucro_liquido = lucro_operacional + investimentos
        geracao_caixa = receita + entradas_nao_operacionais + custos_variaveis + despesas_fixas + investimentos + saidas_nao_operacionais

        # Ponto de Equilíbrio
        ponto_equilibrio = self._calcular_ponto_equilibrio(dados_3_meses, lucro_operacional)

        # Dados do mês anterior (para análise horizontal)
        if mes_anterior:
            receita_ant = self.indicadores.calcular_nivel_lucros(mes_anterior, self.CATEGORIAS_RECEITA)
            custos_variaveis_ant = self.indicadores.calcular_nivel_lucros(mes_anterior, self.CATEGORIAS_CUSTOS_VARIAVEIS)
            despesas_fixas_ant = self.indicadores.calcular_nivel_lucros(mes_anterior, self.CATEGORIAS_DESPESAS_FIXAS)
            investimentos_ant = self.indicadores.calcular_nivel_lucros(mes_anterior, self.CATEGORIAS_INVESTIMENTOS)
            entradas_nao_operacionais_ant = self.indicadores.calcular_nivel_lucros(mes_anterior, self.CATEGORIAS_ENTRADAS_NAO_OPERACIONAIS)
            saidas_nao_operacionais_ant = self.indicadores.calcular_nivel_lucros(mes_anterior, self.CATEGORIAS_SAIDAS_NAO_OPERACIONAIS)

            lucro_bruto_ant = receita_ant + custos_variaveis_ant
            lucro_operacional_ant = lucro_bruto_ant + despesas_fixas_ant
            lucro_liquido_ant = lucro_operacional_ant + investimentos_ant
            geracao_caixa_ant = receita_ant + entradas_nao_operacionais_ant + custos_variaveis_ant + despesas_fixas_ant + investimentos_ant + saidas_nao_operacionais_ant
        else:
            receita_ant = custos_variaveis_ant = despesas_fixas_ant = investimentos_ant = entradas_nao_operacionais_ant = saidas_nao_operacionais_ant = 0
            lucro_bruto_ant = lucro_operacional_ant = lucro_liquido_ant = geracao_caixa_ant = 0

        # Análise Vertical (% em relação à Receita do mês atual)
        av_receita = 100 if receita else 0
        av_lucro_bruto = round((lucro_bruto / receita) * 100, 2) if receita else 0
        av_lucro_operacional = round((lucro_operacional / receita) * 100, 2) if receita else 0
        av_lucro_liquido = round((lucro_liquido / receita) * 100, 2) if receita else 0
        av_geracao_caixa = round((geracao_caixa / receita) * 100, 2) if receita else 0

        # Análise Horizontal (variação em relação ao mês anterior)
        ah_lucro_bruto = AnalisesFinanceiras.calcular_analise_horizontal(lucro_bruto, lucro_bruto_ant) if mes_anterior else 0
        ah_lucro_operacional = AnalisesFinanceiras.calcular_analise_horizontal(lucro_operacional, lucro_operacional_ant) if mes_anterior else 0
        ah_lucro_liquido = AnalisesFinanceiras.calcular_analise_horizontal(lucro_liquido, lucro_liquido_ant) if mes_anterior else 0
        ah_geracao_caixa = AnalisesFinanceiras.calcular_analise_horizontal(geracao_caixa, geracao_caixa_ant) if mes_anterior else 0

        # Notas automatizadas
        notas = []
        if av_lucro_operacional < 10 and receita > 0:
            notas.append(f"Lucro Operacional baixo ({av_lucro_operacional:.2f}% da receita): margens operacionais podem estar comprimidas.")
        if abs(ah_geracao_caixa) > 20 and mes_anterior:
            notas.append(f"Variação expressiva na Geração de Caixa ({ah_geracao_caixa:.2f}%): fluxo de caixa instável, analise entradas/saídas.")
        if lucro_bruto > 0 and lucro_liquido < lucro_bruto * 0.5:
            notas.append("Lucro Líquido menor que 50% do Lucro Bruto: investimentos ou despesas estão impactando fortemente o resultado.")
        if ponto_equilibrio > sum(dados_3_meses["Receita"]) / 3:
            notas.append(f"Ponto de Equilíbrio (R$ {ponto_equilibrio:,.2f}) acima da receita média dos últimos 3 meses: risco de prejuízo iminente.")
        if geracao_caixa < 0 and av_geracao_caixa < -10:
            notas.append(f"Geração de Caixa negativa ({av_geracao_caixa:.2f}% da receita): liquidez em alerta, avalie saídas não operacionais.")

        return {
            "Empresa": self.nome_cliente,
            "Receita": receita,
            "Lucro Bruto": lucro_bruto,
            "Lucro Operacional": lucro_operacional,
            "Lucro Líquido": lucro_liquido,
            "Geração de Caixa": geracao_caixa,
            "Ponto de Equilíbrio": ponto_equilibrio,
            "AV Receita": av_receita,
            "AV Lucro Bruto": av_lucro_bruto,
            "AV Lucro Operacional": av_lucro_operacional,
            "AV Lucro Líquido": av_lucro_liquido,
            "AV Geração de Caixa": av_geracao_caixa,
            "AH Lucro Bruto": ah_lucro_bruto,
            "AH Lucro Operacional": ah_lucro_operacional,
            "AH Lucro Líquido": ah_lucro_liquido,
            "AH Geração de Caixa": ah_geracao_caixa,
            "Notas": notas,
            "Dados 3 Meses": dados_3_meses  # Para o gráfico
        }