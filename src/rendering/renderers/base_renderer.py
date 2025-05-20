#src/rendering/renderers/base_renderer.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader
import os

class BaseRenderer(ABC):
    """Classe base para renderizadores de relatórios."""
    
    def __init__(self):
        # Configuração do ambiente Jinja2
        templates_dir = os.path.abspath("templates")
        self.env = Environment(
            loader=FileSystemLoader(templates_dir), 
            autoescape=True
        )
        
        # Registrar filtros personalizados
        self.env.filters['format_currency'] = self._format_currency
        self.env.filters['format_percentage'] = self._format_percentage
        self.env.filters['format_number'] = self._format_number
    
    def _format_currency(self, value):
        """Formata valores monetários no padrão brasileiro (R$ 1.234.567,89)."""
        if value is None:
            return "R$ 0,00"
        # Converte para float e garante duas casas decimais
        value = float(value)
        # Determina o sinal
        sign = "-" if value < 0 else ""
        # Trabalha com o valor absoluto
        abs_value = abs(value)
        # Separa parte inteira e decimal
        integer_part = int(abs_value)
        decimal_part = round((abs_value - integer_part) * 100)
        # Formata a parte inteira com pontos como separadores de milhares
        integer_str = f"{integer_part:,}".replace(",", ".")
        # Garante que a parte decimal tenha dois dígitos
        decimal_str = f"{decimal_part:02d}"
        # Combina as partes
        return f"R$ {sign}{integer_str},{decimal_str}"
    
    def _format_percentage(self, value):
        """Formata valores percentuais no padrão brasileiro."""
        if value is None:
            return "0,0%"
        return f"{value:,.1f}%".replace('.', ',')
    
    def _format_number(self, value, decimals=2):
        """Formata números com casas decimais específicas no padrão brasileiro."""
        if value is None:
            return "0"
        return f"{value:,.{decimals}f}".replace('.', ',')
    
    @abstractmethod
    def render(self, data: Any, cliente_nome: str, mes_nome: str, ano: int) -> str:
        """
        Renderiza os dados do relatório em HTML.
        
        Args:
            data: Dados específicos do relatório
            cliente_nome: Nome do cliente
            mes_nome: Nome do mês
            ano: Ano do relatório
            
        Returns:
            HTML formatado
        """
        pass