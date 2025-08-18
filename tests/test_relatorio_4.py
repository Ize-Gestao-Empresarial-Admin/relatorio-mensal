# test_relatorio_4.py
from datetime import date
import json
from src.database.db_utils import DatabaseConnection
from src.core.indicadores import Indicadores
from src.core.relatorios.relatorio_4 import Relatorio4

def testar_relatorio(id_cliente: int, mes: date):
    db_connection = DatabaseConnection()
    # Convertemos o ID para lista para funcionar com o operador ANY
    id_cliente_list = [id_cliente] if isinstance(id_cliente, int) else id_cliente
    indicadores = Indicadores(id_cliente_list, db_connection)
    relatorio = Relatorio4(indicadores, "Teste Cliente")
    
    resultado = relatorio.gerar_relatorio(mes)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    id_cliente = 122
    mes = date(2025, 6, 1)
    testar_relatorio(id_cliente, mes)