# test_relatorio_6.py
from datetime import date
import json
from src.database.db_utils import DatabaseConnection
from src.core.indicadores import Indicadores
from src.core.relatorios.relatorio_6 import Relatorio6

def testar_relatorio(id_cliente: int, mes: date):
    db_connection = DatabaseConnection()
    indicadores = Indicadores(id_cliente, db_connection)
    relatorio = Relatorio6(indicadores, "GrupoRedesul")
    
    resultado, notas = relatorio.gerar_relatorio(mes)
    print(json.dumps({"resultado": resultado, "notas": notas}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    id_cliente = 106
    mes = date(2025, 4, 1)  # Março de 2025
    testar_relatorio(id_cliente, mes)