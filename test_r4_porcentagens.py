# test_r4_porcentagens.py
from datetime import date
import json
from src.database.db_utils import DatabaseConnection
from src.core.porcentagens.r4_porcentagens import R4Porcentagens

def testar_porcentagens(id_cliente: int, mes: date):
    db_connection = DatabaseConnection()
    porcentagens = R4Porcentagens(id_cliente, db_connection)

    print("Lucro Líquido:")
    lucro_liquido = porcentagens.calcular_porcentagens_lucro_liquido(mes) #[:3] # chama so os 3 primeiros - não sei aplica a esse
    print(json.dumps(lucro_liquido, indent=2, ensure_ascii=False))

    print("Entradas Não Operacionais:")
    entradas_nao_operacionais = porcentagens.calcular_porcentagens_entradas_nao_operacionais(mes)
    print(json.dumps(entradas_nao_operacionais, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    id_cliente = 85
    mes = date(2025, 3, 1)
    testar_porcentagens(id_cliente, mes)