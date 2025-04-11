# tests/test_analises.py
from src.core.analises import AnalisesFinanceiras

def test_calcular_analise_horizontal():
    # Teste com valores normais
    assert AnalisesFinanceiras.calcular_analise_horizontal(200, 100) == 100.0
    # Teste com valor anterior zero
    assert AnalisesFinanceiras.calcular_analise_horizontal(200, 0) == 0.0
    # Teste com redução
    assert AnalisesFinanceiras.calcular_analise_horizontal(50, 100) == -50.0

def test_calcular_analise_vertical():
    # Teste com valores normais
    assert AnalisesFinanceiras.calcular_analise_vertical(50, 200) == 25.0
    # Teste com total zero
    assert AnalisesFinanceiras.calcular_analise_vertical(50, 0) == 0.0