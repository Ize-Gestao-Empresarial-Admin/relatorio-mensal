# src/core/relatorios/relatorio_1.py
from datetime import date
from typing import Optional
from src.core.indicadores import Indicadores
from src.core.relatorios.deprecated.analises import AnalisesFinanceiras

# na nova refatoracao, os nomes serao categoria_peso_1, categoria_peso_2, etc
# para colocar os pesos de cada categoria, posso puxar em forma de lista as iteranco com base no que foi retornado no bd, como 1 valor - maior peso, 2 valor - 2 maior peso etc
class Relatorio1:
    CATEGORIA_RECEITAS = "3. Receitas"
    CATEGORIA_CUSTOS_VARIAVEIS = "4. Custos Variáveis"
    CATEGORIA_DESPESAS_FIXAS = "5. Despesas Fixas"
    CATEGORIA_INVESTIMENTOS = "6. Investimentos"

    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> dict:
        """Gera o relatório financeiro 1."""
        # Cálculos do mês atual
        receita_atual = self.indicadores.calcular_nivel_1(mes_atual, [self.CATEGORIA_RECEITAS])
        custos_variaveis_atual = self.indicadores.calcular_nivel_1(mes_atual, [self.CATEGORIA_CUSTOS_VARIAVEIS])
        despesas_fixas_atual = self.indicadores.calcular_nivel_1(mes_atual, [self.CATEGORIA_DESPESAS_FIXAS])
        investimentos_atual = self.indicadores.calcular_nivel_1(mes_atual, [self.CATEGORIA_INVESTIMENTOS])
        lucro_operacional_atual = self.indicadores.calcular_nivel_1(
            mes_atual, 
            categorias=[self.CATEGORIA_RECEITAS, self.CATEGORIA_CUSTOS_VARIAVEIS, self.CATEGORIA_DESPESAS_FIXAS]
        )

        # Cálculos do mês anterior - se fornecido
        if mes_anterior:
            receita_anterior = self.indicadores.calcular_nivel_1(mes_anterior, [self.CATEGORIA_RECEITAS])
            custos_variaveis_anterior = self.indicadores.calcular_nivel_1(mes_anterior, [self.CATEGORIA_CUSTOS_VARIAVEIS])
            despesas_fixas_anterior = self.indicadores.calcular_nivel_1(mes_anterior, [self.CATEGORIA_DESPESAS_FIXAS])
            investimentos_anterior = self.indicadores.calcular_nivel_1(mes_anterior, [self.CATEGORIA_INVESTIMENTOS])
            lucro_operacional_anterior = self.indicadores.calcular_nivel_1(
                mes_anterior, 
                categorias=[self.CATEGORIA_RECEITAS, self.CATEGORIA_CUSTOS_VARIAVEIS, self.CATEGORIA_DESPESAS_FIXAS]
            )
        else:
            receita_anterior = custos_variaveis_anterior = despesas_fixas_anterior = investimentos_anterior = lucro_operacional_anterior = 0

        # Análise Vertical
        av_receita = 100 if receita_atual else 0
        av_custos_variaveis = round((custos_variaveis_atual / receita_atual) * 100, 2) if receita_atual else 0
        av_despesas_fixas = round((despesas_fixas_atual / receita_atual) * 100, 2) if receita_atual else 0
        av_lucro_operacional = round((lucro_operacional_atual / receita_atual) * 100, 2) if receita_atual else 0

        # Análise Horizontal
        ah_receita = AnalisesFinanceiras.calcular_analise_horizontal(receita_atual, receita_anterior) if mes_anterior else 0
        ah_custos_variaveis = AnalisesFinanceiras.calcular_analise_horizontal(custos_variaveis_atual, custos_variaveis_anterior) if mes_anterior else 0
        ah_despesas_fixas = AnalisesFinanceiras.calcular_analise_horizontal(despesas_fixas_atual, despesas_fixas_anterior) if mes_anterior else 0
        ah_investimentos = AnalisesFinanceiras.calcular_analise_horizontal(investimentos_atual, investimentos_anterior) if mes_anterior else 0
        ah_lucro_operacional = AnalisesFinanceiras.calcular_analise_horizontal(lucro_operacional_atual, lucro_operacional_anterior) if mes_anterior else 0

        return {
            "Empresa": self.nome_cliente,
            "Receita": receita_atual,
            "Custos Variáveis": custos_variaveis_atual,
            "Despesas Fixas": despesas_fixas_atual,
            "Investimentos": investimentos_atual,
            "Lucro Operacional": lucro_operacional_atual,
            "AV Custos Variáveis": av_custos_variaveis,
            "AV Despesas Fixas": av_despesas_fixas,
            "AV Lucro Operacional": av_lucro_operacional,
            "AH Receita": ah_receita,
            "AH Custos Variáveis": ah_custos_variaveis,
            "AH Despesas Fixas": ah_despesas_fixas,
            "AH Lucro Operacional": ah_lucro_operacional
        }
        
        # inserir nota do consultor puxando alguma variavel dinamica (de a 1 a 6)
        