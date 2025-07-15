# test_relatorio_6.py
from datetime import date
import json
from src.database.db_utils import DatabaseConnection
from src.core.indicadores import Indicadores
from src.core.relatorios.relatorio_6 import Relatorio6

def testar_relatorio(cliente_ids: list, mes: date, display_cliente_nome: str = "Cliente Teste"):
    db_connection = DatabaseConnection()
    indicadores = Indicadores(cliente_ids, db_connection)
    relatorio = Relatorio6(indicadores, display_cliente_nome)
    
    resultado, notas = relatorio.gerar_relatorio(mes)
    print(json.dumps({"resultado": resultado, "notas": notas}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    cliente_ids = [236]  # Você pode adicionar mais IDs conforme necessário (atual: AR Advocacia)
    mes = date(2025, 5, 1)
    testar_relatorio(cliente_ids, mes)