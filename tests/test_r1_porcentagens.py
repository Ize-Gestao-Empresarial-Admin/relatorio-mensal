# test_r1_porcentagens.py
from datetime import date
import json
from src.database.db_utils import DatabaseConnection
from src.core.porcentagens.r1_porcentagens import R1Porcentagens

def testar_porcentagens(id_cliente: int, mes: date):
    db_connection = DatabaseConnection()
    porcentagens = R1Porcentagens(id_cliente, db_connection)

    print("Custos Variáveis:")
    custos_variaveis = porcentagens.calcular_porcentagens_custos_variaveis(mes)[:3] # chama so os 3 primeiros
    print(json.dumps(custos_variaveis, indent=2, ensure_ascii=False))

    print("Receitas:")
    receitas = porcentagens.calcular_porcentagens_receitas(mes)[:3] # chama so os 3 primeiros
    print(json.dumps(receitas, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    id_cliente = 85
    mes = date(2025, 3, 1)
    testar_porcentagens(id_cliente, mes)