# test_relatorio_7.py
from datetime import date
import json
from src.database.db_utils import DatabaseConnection
from src.core.indicadores import Indicadores
from src.core.relatorios.relatorio_7 import Relatorio7

def testar_relatorio(cliente_ids: list, mes: date, display_cliente_nome: str = "Cliente Teste"):
    db_connection = DatabaseConnection()
    indicadores = Indicadores(cliente_ids, db_connection)
    relatorio = Relatorio7(indicadores, display_cliente_nome)
    
    resultado = relatorio.gerar_relatorio(mes)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    cliente_ids = [89]  # Você pode adicionar mais IDs conforme necessário (atual: levens)
    mes = date(2025, 5, 1)
    testar_relatorio(cliente_ids, mes)