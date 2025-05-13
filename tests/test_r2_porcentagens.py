# test_r2_porcentagens.py
from datetime import date
import json
from src.database.db_utils import DatabaseConnection
from src.core.porcentagens.r2_porcentagens import R2Porcentagens

def testar_porcentagens(id_cliente: int, mes: date):
    db_connection = DatabaseConnection()
    porcentagens = R2Porcentagens(id_cliente, db_connection)

    print("Lucro Bruto:")
    lucro_bruto = porcentagens.calcular_porcentagens_lucro_bruto(mes)[:3] # chama so os 3 primeiros
    print(json.dumps(lucro_bruto, indent=2, ensure_ascii=False))

    print("Despesas Fixas:")
    despesas_fixas = porcentagens.calcular_porcentagens_despesas_fixas(mes)[:3] # chama so os 3 primeiros
    print(json.dumps(despesas_fixas, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    id_cliente = 85
    mes = date(2025, 3, 1)
    testar_porcentagens(id_cliente, mes)