#src/core/relatorios/relatorio_8.py
#Notas do consultor
from datetime import date
from typing import Optional, Dict, Any

class Relatorio8:
    def __init__(self, indicadores, nome_cliente: str):
        """Inicializa a classe Relatorio8 para elaborar Notas do Consultor.

        """
        self.nome_cliente = nome_cliente
        self.analise_text = ""

    def salvar_analise(self, mes_atual: date, analise_text: str) -> None:
        """Salva o texto da análise (nota do consultor).

        Args:
            analise_text: Texto da análise em HTML.
        """
        self.analise_text = analise_text if analise_text else "<p>Nenhuma nota fornecida.</p>"

    def gerar_relatorio(self, mes_atual: date) -> tuple[list, Dict[str, Any]]:
        """Gera os dados do Relatório 8 (Nota do Consultor).

        Args:
            mes_atual: Data do mês atual.

        Returns:
            Tupla com lista vazia (sem dados estruturados) e dicionário com a nota em HTML.
        """
        return [], {"nota_consultor": self.analise_text}