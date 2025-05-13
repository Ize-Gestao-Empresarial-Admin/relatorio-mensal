# test_r3_porcentagens.py
from datetime import date
import json
from src.database.db_utils import DatabaseConnection
from src.core.porcentagens.r3_porcentagens import R3Porcentagens

def testar_porcentagens(id_cliente: int, mes: date):
    db_connection = DatabaseConnection()
    porcentagens = R3Porcentagens(id_cliente, db_connection)

    print("Lucro Operacional:")
    lucro_operacional = porcentagens.calcular_porcentagens_lucro_operacional(mes)[:3] # chama so os 3 primeiros
    print(json.dumps(lucro_operacional, indent=2, ensure_ascii=False))

    print("Investimentos:")
    investimentos = porcentagens.calcular_porcentagens_investimentos(mes)
    print(json.dumps(investimentos, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    id_cliente = 85
    mes = date(2025, 3, 1)
    testar_porcentagens(id_cliente, mes)