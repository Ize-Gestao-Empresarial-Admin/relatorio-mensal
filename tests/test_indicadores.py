# tests/test_indicadores.py
from datetime import date
from unittest.mock import Mock, patch
import pandas as pd
from src.core.indicadores import Indicadores

def test_calcular_nivel_1():
    # Mock da conexão ao banco
    db_mock = Mock()
    db_mock.execute_query.return_value = pd.DataFrame({"total": [500.0]})
    
    indicadores = Indicadores(id_cliente=1, db_connection=db_mock)
    resultado = indicadores.calcular_nivel_1(date(2025, 3, 1), ["3. Receitas"])
    
    assert resultado == 500.0
    db_mock.execute_query.assert_called_once()

