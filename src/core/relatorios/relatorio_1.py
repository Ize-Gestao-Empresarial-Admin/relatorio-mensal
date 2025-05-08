from datetime import date
from typing import Optional, Dict, Any
from src.core.indicadores import Indicadores
from src.core.analises import AnalisesFinanceiras

class Relatorio1:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> Dict[str, Any]:
        """Gera o relatório financeiro 1 com receitas, custos variáveis, suas principais categorias e análises."""
        
        # Receitas - Pegar as 5 maiores categorias
        receitas_resultado = self.indicadores.calcular_receitas_fc(mes_atual, '3.%')
        receita_atual = sum(r['total_categoria'] for r in receitas_resultado) if receitas_resultado else 0
        
        # Custos Variáveis - Pegar as 5 maiores categorias
        custos_variaveis_resultado = self.indicadores.calcular_custos_variaveis_fc(mes_atual, '4.%')
        custos_variaveis_atual = sum(r['total_categoria'] for r in custos_variaveis_resultado) if custos_variaveis_resultado else 0

        # Inicializar dicionário de retorno
        resultado = {
            "Empresa": self.nome_cliente,
            "Receita": receita_atual,
            "Custos Variáveis": custos_variaveis_atual,
        }

        # Adicionar categorias de receitas com pesos individuais (até 5)
        for i in range(5):
            if i < len(receitas_resultado):
                resultado[f"categoria_peso_{i+1}_receita"] = receitas_resultado[i]['categoria_nivel_3']
                resultado[f"total_{i+1}_receita"] = receitas_resultado[i]['total_categoria']
            else:
                resultado[f"categoria_peso_{i+1}_receita"] = None
                resultado[f"total_{i+1}_receita"] = 0

        # Adicionar categorias de custos variáveis com pesos individuais (até 5)
        for i in range(5):
            if i < len(custos_variaveis_resultado):
                resultado[f"categoria_peso_{i+1}_custo"] = custos_variaveis_resultado[i]['nivel_2']
                resultado[f"total_{i+1}_custo"] = custos_variaveis_resultado[i]['total_categoria']
            else:
                resultado[f"categoria_peso_{i+1}_custo"] = None
                resultado[f"total_{i+1}_custo"] = 0

        # Cálculos do mês anterior - se fornecido
        if mes_anterior:
            receitas_anterior_resultado = self.indicadores.calcular_receitas_fc(mes_anterior, '3.%')
            receita_anterior = sum(r['total_categoria'] for r in receitas_anterior_resultado) if receitas_anterior_resultado else 0
            
            custos_variaveis_anterior_resultado = self.indicadores.calcular_custos_variaveis_fc(mes_anterior, '4.%')
            custos_variaveis_anterior = sum(r['total_categoria'] for r in custos_variaveis_anterior_resultado) if custos_variaveis_anterior_resultado else 0
        else:
            receita_anterior = custos_variaveis_anterior = 0

        # Análise Vertical
        av_receita = 100 if receita_atual else 0
        av_custos_variaveis = round((custos_variaveis_atual / receita_atual) * 100, 2) if receita_atual else 0

        # Análise Horizontal
        ah_receita = AnalisesFinanceiras.calcular_analise_horizontal(receita_atual, receita_anterior) if mes_anterior else 0
        ah_custos_variaveis = AnalisesFinanceiras.calcular_analise_horizontal(custos_variaveis_atual, custos_variaveis_anterior) if mes_anterior else 0

        # Notas Automatizadas sobre Custos Variáveis
        notas_automatizadas = (
            "Os custos variáveis são gastos diretamente associados à operação da empresa, como matéria-prima, "
            "comissões de vendas e custos de produção. Eles tendem a acompanhar o movimento das receitas, "
            "aumentando quando a receita cresce e diminuindo em períodos de menor atividade."
        )

        # Adicionar análises ao dicionário
        resultado.update({
            "AV Receita": av_receita,
            "AV Custos Variáveis": av_custos_variaveis,
            "AH Receita": ah_receita,
            "AH Custos Variáveis": ah_custos_variaveis,
            "Notas Automatizadas": notas_automatizadas
        })

        return resultado