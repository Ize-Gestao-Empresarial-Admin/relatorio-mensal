# src/core/relatorios/relatorio_2.py
from datetime import date
from typing import Optional
from src.core.indicadores import Indicadores
from src.core.analises import AnalisesFinanceiras

class Relatorio2:
    CATEGORIAS_FATURAMENTO = ["Receita de Vendas de Produtos", "Receita de Prestação de Serviços"]
    CATEGORIAS_deducao_receita_bruta = ["Descontos Incondicionais", "ICMS", "PIS", "COFINS", "ISS",
                          "Simples Nacional", "Outros Tributos de Deduções de Vendas", "Devoluções de Vendas"]
    CATEGORIAS_CUSTOS_VARIAVEIS = ["Custos com Produtos e Serviços", "Custos Comerciais"]
    CATEGORIAS_DESPESAS_FIXAS = ["Despesas Administrativas", "Despesas com Pessoal",
                                 "Despesas com Serviços de Terceiros", "Despesas com Materiais e Equipamentos",
                                 "Despesas de Marketing", "Despesas com Desenvolvimento Empresarial"]
    CATEGORIAS_RECEITAS_FINANCEIRAS = ["Receitas Financeiras", "Rendimentos de Aplicações"]
    CATEGORIAS_DESPESAS_FINANCEIRAS = ["Despesas Financeiras", "Juros Bancários"]
    CATEGORIAS_IMPOSTOS = ["IRPJ", "CSLL", "Tributos sobre o Lucro Não Identificados" ]
    CATEGORIAS_INVESTIMENTOS = ["Investimentos em Bens Materiais", "Investimento em Imobilizado", "Investimento de Intangíveis"]
    CATEGORIAS_ENTRADAS_NAO_OPERACIONAIS = ["Empréstimos bancários","Venda de Imobilizados", "Devolução de Pagamentos", "Outras entradas não operacionais", "7.1.6 Outras Entradas não Operacionais"]
    CATEGORIAS_SAIDAS_NAO_OPERACIONAIS = ["Perdas Jurídicas", "Aplicações Financeiras", "Pagamento de Empréstimos",
                                          "Dívidas Passadas","Outras saídas não operacionais"]
    CATEGORIAS_APORTE = ["Capitalização dos sócios"]
    CATEGORIAS_DISTRIBUICAO_LUCROS = ["Distribuição de Lucros"]

    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> dict:
        """Gera o relatório financeiro 2 - Análise por Competência (DRE)."""
        # Cálculos do mês atual 
        faturamento = self.indicadores.calcular_categoria_dre(mes_atual, self.CATEGORIAS_FATURAMENTO)
        deducao_receita_bruta = self.indicadores.calcular_categoria_dre(mes_atual, self.CATEGORIAS_deducao_receita_bruta)
        custos_variaveis = self.indicadores.calcular_categoria_dre(mes_atual, self.CATEGORIAS_CUSTOS_VARIAVEIS)
        despesas_fixas = self.indicadores.calcular_categoria_dre(mes_atual, self.CATEGORIAS_DESPESAS_FIXAS)
        ebitda = faturamento + deducao_receita_bruta + custos_variaveis + despesas_fixas
        
        # Lucro Operacional 
        receitas_financeiras = self.indicadores.calcular_categoria_dre(mes_atual, self.CATEGORIAS_RECEITAS_FINANCEIRAS)
        despesas_financeiras = self.indicadores.calcular_categoria_dre(mes_atual, self.CATEGORIAS_DESPESAS_FINANCEIRAS)
        impostos = self.indicadores.calcular_categoria_dre(mes_atual, self.CATEGORIAS_IMPOSTOS)
        lucro_operacional = (faturamento + deducao_receita_bruta + custos_variaveis + despesas_fixas + 
                             receitas_financeiras + despesas_financeiras + impostos) # faturamento = receita operacional

        # Lucro Líquido 
        investimentos = self.indicadores.calcular_categoria_dre(mes_atual, self.CATEGORIAS_INVESTIMENTOS)
        entradas_nao_operacionais = self.indicadores.calcular_categoria_dre(mes_atual, self.CATEGORIAS_ENTRADAS_NAO_OPERACIONAIS)
        saidas_nao_operacionais = self.indicadores.calcular_categoria_dre(mes_atual, self.CATEGORIAS_SAIDAS_NAO_OPERACIONAIS)
        aporte = self.indicadores.calcular_categoria_dre(mes_atual, self.CATEGORIAS_APORTE)
        distribuicao_lucros = self.indicadores.calcular_categoria_dre(mes_atual, self.CATEGORIAS_DISTRIBUICAO_LUCROS)
        lucro_liquido = (faturamento + deducao_receita_bruta + custos_variaveis + despesas_fixas + 
                         receitas_financeiras + despesas_financeiras + impostos + 
                         investimentos + entradas_nao_operacionais + saidas_nao_operacionais +  
                         aporte + distribuicao_lucros) # faturamento = receita operacional

        # Custo Produto e Serviço (mantido como extra para o indicador solicitado)
        custo_produto_servico = self.indicadores.calcular_categoria_dre(mes_atual, ["Custos com Produtos e Serviços"])

        # Análise Vertical
        av_faturamento = 100 if faturamento else 0
        av_deducao_receita_bruta = round((deducao_receita_bruta / faturamento) * 100, 2) if faturamento else 0
        av_custos_variaveis = round((custos_variaveis / faturamento) * 100, 2) if faturamento else 0
        av_custo_produto_servico = round((custo_produto_servico / faturamento) * 100, 2) if faturamento else 0
        av_despesas_fixas = round((despesas_fixas / faturamento) * 100, 2) if faturamento else 0
        av_ebitda = round((ebitda / faturamento) * 100, 2) if faturamento else 0
        av_lucro_operacional = round((lucro_operacional / faturamento) * 100, 2) if faturamento else 0
        av_lucro_liquido = round((lucro_liquido / faturamento) * 100, 2) if faturamento else 0

        # Cálculos do mês anterior (se fornecido)
        if mes_anterior:
            faturamento_ant = self.indicadores.calcular_categoria_dre(mes_anterior, self.CATEGORIAS_FATURAMENTO)
            deducao_receita_bruta_ant = self.indicadores.calcular_categoria_dre(mes_anterior, self.CATEGORIAS_deducao_receita_bruta)
            custos_variaveis_ant = self.indicadores.calcular_categoria_dre(mes_anterior, self.CATEGORIAS_CUSTOS_VARIAVEIS)
            despesas_fixas_ant = self.indicadores.calcular_categoria_dre(mes_anterior, self.CATEGORIAS_DESPESAS_FIXAS)
            ebitda_ant = faturamento_ant + deducao_receita_bruta_ant + custos_variaveis_ant + despesas_fixas_ant
            receitas_financeiras_ant = self.indicadores.calcular_categoria_dre(mes_anterior, self.CATEGORIAS_RECEITAS_FINANCEIRAS)
            despesas_financeiras_ant = self.indicadores.calcular_categoria_dre(mes_anterior, self.CATEGORIAS_DESPESAS_FINANCEIRAS)
            impostos_ant = self.indicadores.calcular_categoria_dre(mes_anterior, self.CATEGORIAS_IMPOSTOS)
            lucro_operacional_ant = (faturamento_ant + deducao_receita_bruta_ant + custos_variaveis_ant + despesas_fixas_ant + 
                                     receitas_financeiras_ant + despesas_financeiras_ant + impostos_ant)
            investimentos_ant = self.indicadores.calcular_categoria_dre(mes_anterior, self.CATEGORIAS_INVESTIMENTOS)
            entradas_nao_operacionais_ant = self.indicadores.calcular_categoria_dre(mes_anterior, self.CATEGORIAS_ENTRADAS_NAO_OPERACIONAIS)
            saidas_nao_operacionais_ant = self.indicadores.calcular_categoria_dre(mes_anterior, self.CATEGORIAS_SAIDAS_NAO_OPERACIONAIS)
            aporte_ant = self.indicadores.calcular_categoria_dre(mes_anterior, self.CATEGORIAS_APORTE)
            distribuicao_lucros_ant = self.indicadores.calcular_categoria_dre(mes_anterior, self.CATEGORIAS_DISTRIBUICAO_LUCROS)
            lucro_liquido_ant = (faturamento_ant + deducao_receita_bruta_ant + custos_variaveis_ant + despesas_fixas_ant + 
                                 receitas_financeiras_ant + despesas_financeiras_ant + impostos_ant + 
                                 investimentos_ant + entradas_nao_operacionais_ant + saidas_nao_operacionais_ant + 
                                 aporte_ant + distribuicao_lucros_ant)
            custo_produto_servico_ant = self.indicadores.calcular_categoria_dre(mes_anterior, ["Custos com Produtos e Serviços"])
        else:
            faturamento_ant = deducao_receita_bruta_ant = custos_variaveis_ant = custo_produto_servico_ant = despesas_fixas_ant = 0
            ebitda_ant = lucro_operacional_ant = lucro_liquido_ant = 0
            receitas_financeiras_ant = despesas_financeiras_ant = impostos_ant = 0
            investimentos_ant = entradas_nao_operacionais_ant = saidas_nao_operacionais_ant = aporte_ant = distribuicao_lucros_ant = 0

        # Análise Horizontal
        ah_faturamento = AnalisesFinanceiras.calcular_analise_horizontal(faturamento, faturamento_ant) if mes_anterior else 0
        ah_deducao_receita_bruta = AnalisesFinanceiras.calcular_analise_horizontal(deducao_receita_bruta, deducao_receita_bruta_ant) if mes_anterior else 0
        ah_custos_variaveis = AnalisesFinanceiras.calcular_analise_horizontal(custos_variaveis, custos_variaveis_ant) if mes_anterior else 0
        ah_despesas_fixas = AnalisesFinanceiras.calcular_analise_horizontal(despesas_fixas, despesas_fixas_ant) if mes_anterior else 0
        ah_ebitda = AnalisesFinanceiras.calcular_analise_horizontal(ebitda, ebitda_ant) if mes_anterior else 0
        ah_lucro_operacional = AnalisesFinanceiras.calcular_analise_horizontal(lucro_operacional, lucro_operacional_ant) if mes_anterior else 0
        ah_lucro_liquido = AnalisesFinanceiras.calcular_analise_horizontal(lucro_liquido, lucro_liquido_ant) if mes_anterior else 0

        return {
            "Empresa": self.nome_cliente,
            "Faturamento": faturamento,
            "Dedutíveis": deducao_receita_bruta,
            "Custo Variável": custos_variaveis,
            "Custo Produto e Serviço": custo_produto_servico,
            "Despesa Fixa": despesas_fixas,
            "EBITDA": ebitda,
            "Lucro Operacional": lucro_operacional,
            "Lucro Líquido": lucro_liquido,
            "AV Faturamento": av_faturamento,
            "AV Dedutíveis": av_deducao_receita_bruta,
            "AV Custo Variável": av_custos_variaveis,
            "AV Custo Produto e Serviço": av_custo_produto_servico,
            "AV Despesa Fixa": av_despesas_fixas,
            "AV EBITDA": av_ebitda,
            "AV Lucro Operacional": av_lucro_operacional,
            "AV Lucro Líquido": av_lucro_liquido,
            "AH Faturamento": ah_faturamento,
            "AH Dedutíveis": ah_deducao_receita_bruta,
            "AH Custo Variável": ah_custos_variaveis,
            "AH Despesa Fixa": ah_despesas_fixas,
            "AH EBITDA": ah_ebitda,
            "AH Lucro Operacional": ah_lucro_operacional,
            "AH Lucro Líquido": ah_lucro_liquido
        }