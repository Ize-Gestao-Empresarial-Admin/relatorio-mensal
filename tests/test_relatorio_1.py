# test_relatorio_1.py
from datetime import date
from typing import Optional, List, Dict, Any
import json
from dateutil.relativedelta import relativedelta
from src.database.db_utils import DatabaseConnection
from src.core.indicadores import Indicadores
from src.core.relatorios.relatorio_1 import Relatorio1

def testar_relatorio(id_cliente: int, mes_atual: date, mes_anterior: Optional[date] = None):
    if mes_anterior is None:
        mes_anterior = mes_atual - relativedelta(months=1)
    
    db_connection = DatabaseConnection()
    indicadores = Indicadores(id_cliente, db_connection)
    relatorio = Relatorio1(indicadores, "Teste Cliente")
    
    resultado = relatorio.gerar_relatorio(mes)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    id_cliente =243
    mes = date(2025, 3, 1)
    testar_relatorio(id_cliente, mes)
    