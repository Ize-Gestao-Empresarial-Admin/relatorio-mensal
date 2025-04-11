# src/core/relatorios/relatorio_5.py
from datetime import date
from src.core.indicadores import Indicadores

class Relatorio5:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente
        # Buscar indicadores dinamicamente com base no id_cliente
        self.indicadores_disponiveis = self.indicadores.buscar_indicadores_disponiveis()

    def gerar_relatorio(self, mes_atual: date) -> dict:
        """Gera o relatório financeiro 5 - Indicadores."""
        dados_indicadores = self.indicadores.calcular_indicadores(mes_atual, self.indicadores_disponiveis)
        
        return {
            "Empresa": self.nome_cliente,
            "Indicadores": dados_indicadores
        }