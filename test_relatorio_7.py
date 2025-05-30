# test_relatorio_7.py
from datetime import date
import json
from src.database.db_utils import DatabaseConnection
from src.core.indicadores import Indicadores
from src.core.relatorios.relatorio_7 import Relatorio7

def testar_relatorio(id_cliente: int, mes: date):
    db_connection = DatabaseConnection()
    indicadores = Indicadores(id_cliente, db_connection)
    relatorio = Relatorio7(indicadores, "Teste Cliente")
    
    resultado = relatorio.gerar_relatorio(mes)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    id_cliente = 243
    mes = date(2025, 3, 1)
    testar_relatorio(id_cliente, mes)