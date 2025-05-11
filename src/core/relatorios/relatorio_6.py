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
            "Os indicadores são calculados com base nos dados do DRE para o mês selecionado. "
        )

        return indicadores_resultado, {"notas": notas_automatizadas}