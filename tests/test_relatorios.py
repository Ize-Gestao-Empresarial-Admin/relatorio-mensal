# tests/test_relatorios.py
from datetime import date
from unittest.mock import Mock
from src.core.relatorios import Relatorios

def test_gerar_relatorio_1():
    # Mock de Indicadores
    indicadores_mock = Mock()
    indicadores_mock.calcular_nivel_1.side_effect = [
        1000.0,  # Receita atual
        -400.0,  # Custos Variáveis atual (negativo)
        -300.0,  # Despesas Fixas atual (negativo)
        100.0,   # Investimentos atual
        300.0,   # Lucro Operacional atual (1000 + (-400) + (-300))
        500.0,   # Receita anterior
        -200.0,  # Custos Variáveis anterior (negativo)
        -150.0,  # Despesas Fixas anterior (negativo)
        50.0,    # Investimentos anterior
        150.0    # Lucro Operacional anterior (500 + (-200) + (-150))
    ]

    relatorios = Relatorios(indicadores_mock, "Empresa XYZ")
    relatorio = relatorios.gerar_relatorio_1(
        mes_atual=date(2025, 3, 1),
        mes_anterior=date(2025, 2, 1)
    )

    # Verificações
    assert relatorio["Empresa"] == "Empresa XYZ"
    assert relatorio["Receita"] == 1000.0
    assert relatorio["Custos Variáveis"] == -400.0
    assert relatorio["Despesas Fixas"] == -300.0
    assert relatorio["Investimentos"] == 100.0
    assert relatorio["Lucro Operacional"] == 300.0
    assert relatorio["AV Custos Variáveis"] == -40.0  # -400 / 1000 * 100
    assert relatorio["AH Receita"] == 100.0  # (1000 - 500) / 500 * 100
    assert relatorio["AH Lucro Operacional"] == 100.0  # (300 - 150) / 150 * 100
    

def test_gerar_relatorio_2_sem_mes_anterior():
    """Testa o relatório 2 sem mês anterior."""
    indicadores_mock = Mock()
    indicadores_mock.calcular_dre.side_effect = [
        1000.0,  # Faturamento
        -100.0,  # Dedução
        -200.0,  # Custos Variáveis
        -150.0,  # Custo Produto e Serviço (extra)
        -300.0,  # Despesas Fixas
        50.0,    # Receitas Financeiras
        -40.0,   # Despesas Financeiras
        -50.0,   # Impostos
        -60.0,   # Investimentos
        30.0,    # Entradas Não Operacionais
        -20.0,   # Saídas Não Operacionais
        10.0,    # Aporte
        -70.0    # Distribuição de Lucros
    ]

    relatorios = Relatorios(indicadores_mock, "Empresa XYZ")
    relatorio = relatorios.gerar_relatorio_2(
        mes_atual=date(2025, 3, 1),
        mes_anterior=None
    )

    # Verificações
    assert relatorio["Faturamento"] == 1000.0
    assert relatorio["Dedutíveis"] == -100.0
    assert relatorio["Custo Variável"] == -200.0
    assert relatorio["Custo Produto e Serviço"] == -150.0
    assert relatorio["Despesa Fixa"] == -300.0
    assert relatorio["EBITDA"] == 400.0  # 1000 - 100 - 200 - 300
    assert relatorio["Lucro Operacional"] == 360.0  # 400 + 50 - 40 - 50
    assert relatorio["Lucro Líquido"] == 250.0  # 360 - 60 + 30 - 20 + 10 - 70
    assert relatorio["AV Faturamento"] == 100.0
    assert relatorio["AV Dedutíveis"] == -10.0
    assert relatorio["AV Custo Variável"] == -20.0
    assert relatorio["AV EBITDA"] == 40.0
    assert relatorio["AH Faturamento"] == 0.0
    
    
    
def test_gerar_relatorio_2_sem_mes_anterior():
    """Testa o relatório 2 sem mês anterior."""
    indicadores_mock = Mock()
    
    # Configure o comportamento do método calcular_categoria_dre
    indicadores_mock.calcular_categoria_dre.side_effect = [
        1000.0,  # Faturamento
        -100.0,  # Dedução
        -200.0,  # Custos Variáveis
        -300.0,  # Despesas Fixas
        50.0,    # Receitas Financeiras
        -40.0,   # Despesas Financeiras
        -50.0,   # Impostos
        -60.0,   # Investimentos
        30.0,    # Entradas Não Operacionais
        -20.0,   # Saídas Não Operacionais
        10.0,    # Aporte
        -70.0,   # Distribuição de Lucros
        -150.0   # Custo Produto e Serviço (extra)
    ]

    relatorios = Relatorios(indicadores_mock, "Empresa XYZ")
    relatorio = relatorios.gerar_relatorio_2(
        mes_atual=date(2025, 3, 1),
        mes_anterior=None
    )
    
    # Verificações permanecem as mesmas