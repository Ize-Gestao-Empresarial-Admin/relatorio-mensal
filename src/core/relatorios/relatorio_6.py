# src/core/relatorios/relatorio_6.py
from datetime import date
from typing import List, Dict, Any
from src.core.indicadores import Indicadores

class Relatorio6:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes: date) -> List[Dict[str, Any]]:
        """Gera o relatório financeiro 6 - Indicadores DRE.

        Args:
            mes: Data do mês a ser calculado.

        Returns:
            Lista de dicionários com indicadores e seus valores.
        """
        # Obter os indicadores calculados
        indicadores_resultado = self.indicadores.calcular_indicadores_dre(mes)

        # Notas automatizadas
        notas_automatizadas = (
             f"No mês, tivemos um total de vendas no montante de R$ xx, seguido das deduções da receita bruta de R$ xx, Custos Variáveis em R$ xx, Despesas Fixas de R$ xx, fechando o mês com um EBITDA de xx% em relação ao faturamento!. \n"
        )

        return indicadores_resultado, {"notas": notas_automatizadas}