# src/core/analises.py
from typing import Optional

#DEPRECATED - 08-05-2025
# contem métodos para análises financeiras - AV, AH
class AnalisesFinanceiras:
    @staticmethod
    def calcular_analise_horizontal(valor_atual: float, valor_anterior: float) -> float:
        """Calcula a análise horizontal entre dois valores.

        Args:
            valor_atual: Valor do período atual.
            valor_anterior: Valor do período anterior.

        Returns:
            Percentual de variação ou 0 se o valor anterior for zero.
        """
        if valor_anterior == 0:
            return 0
        return round(((valor_atual - valor_anterior) / abs(valor_anterior)) * 100, 2)

    # Futuro: adicionar outros métodos como análise vertical ou índices financeiros
    @staticmethod
    def calcular_analise_vertical(valor: float, total: float) -> float:
        """Exemplo de análise vertical para referência futura."""
        if total == 0:
            return 0
        return round((valor / total) * 100, 2)
    
    
    @staticmethod
    def nota_automatica(valor: float) -> Optional[str]:
        """Calcula a nota de acordo com o indicador, faz analises comparativas em texto."""
        pass
    
    # criar criar ah e av especifico deles