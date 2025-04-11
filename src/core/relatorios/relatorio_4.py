# src/core/relatorios/relatorio_4.py
from datetime import date, timedelta
from typing import Optional
from src.core.indicadores import Indicadores

class Relatorio4:
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
        """Calcula dados para os últimos 3 meses fechados antes do mês atual."""
        dados = {
            "Receita": [],
            "Lucro Operacional": [],
            "Geração de Caixa": [],
            "Meses": []
        }
        for i in range(1, meses + 1):
            mes = (mes_atual - timedelta(days=31 * i)).replace(day=1)
            receita = self.indicadores.calcular_nivel_evolucao(mes, self.CATEGORIAS_RECEITA)
            custos_variaveis = self.indicadores.calcular_nivel_evolucao(mes, self.CATEGORIAS_CUSTOS_VARIAVEIS)
            despesas_fixas = self.indicadores.calcular_nivel_evolucao(mes, self.CATEGORIAS_DESPESAS_FIXAS)
            investimentos = self.indicadores.calcular_nivel_evolucao(mes, self.CATEGORIAS_INVESTIMENTOS)
            entradas_nao_oper = self.indicadores.calcular_nivel_evolucao(mes, self.CATEGORIAS_ENTRADAS_NAO_OPERACIONAIS)
            saidas_nao_oper = self.indicadores.calcular_nivel_evolucao(mes, self.CATEGORIAS_SAIDAS_NAO_OPERACIONAIS)

            lucro_operacional = receita + custos_variaveis + despesas_fixas
            geracao_caixa = receita + entradas_nao_oper + custos_variaveis + despesas_fixas + investimentos + saidas_nao_oper

            dados["Receita"].append(receita)
            dados["Lucro Operacional"].append(lucro_operacional)
            dados["Geração de Caixa"].append(geracao_caixa)
            dados["Meses"].append(f"{mes.strftime('%b/%Y')}")
        return dados

    def gerar_relatorio(self, mes_atual: date) -> dict:
        """Gera o relatório financeiro 4 - Evolução."""
        dados_3_meses = self._calcular_dados_meses(mes_atual)

        # Médias
        media_receita = sum(dados_3_meses["Receita"]) / 3 if dados_3_meses["Receita"] else 0
        media_lucro_operacional = sum(dados_3_meses["Lucro Operacional"]) / 3 if dados_3_meses["Lucro Operacional"] else 0
        media_geracao_caixa = sum(dados_3_meses["Geração de Caixa"]) / 3 if dados_3_meses["Geração de Caixa"] else 0

        # Percentuais de Lucro Operacional em relação à Receita
        percentuais_receita = [100] * 3  # Receita sempre 100%
        percentuais_lucro_operacional = [
            round((lo / r) * 100, 2) if r else 0
            for lo, r in zip(dados_3_meses["Lucro Operacional"], dados_3_meses["Receita"])
        ]

        # Caixa Acumulado
        caixa_acumulado = [sum(dados_3_meses["Geração de Caixa"][:i+1]) for i in range(3)]

        return {
            "Empresa": self.nome_cliente,
            "Dados 3 Meses": dados_3_meses,
            "Media Receita": media_receita,
            "Media Lucro Operacional": media_lucro_operacional,
            "Media Geração de Caixa": media_geracao_caixa,
            "Percentuais Receita": percentuais_receita,
            "Percentuais Lucro Operacional": percentuais_lucro_operacional,
            "Caixa Acumulado": caixa_acumulado
        }