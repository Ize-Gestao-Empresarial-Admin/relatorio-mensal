# test_r5_porcentagens.py
from datetime import date
import json
from src.database.db_utils import DatabaseConnection
from src.core.porcentagens.r5_porcentagens import R5Porcentagens

def testar_r5_porcentagens(id_cliente: int, mes: date):
    db_connection = DatabaseConnection()
    r5_porcentagens = R5Porcentagens(id_cliente, db_connection)

    print("Geração de Caixa:")
    resultado = r5_porcentagens.calcular_proporcoes_geracao_de_caixa(mes)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    
    # Calcular o valor total da Geração de Caixa (soma dos valores com Saídas subtraídas)
    total_geracao_de_caixa = sum(
        row["valor"] if row["categoria"] != "Saídas Não Operacionais" else -row["valor"]
        for row in resultado
    )
    print(f"Valor Total da Geração de Caixa: {round(total_geracao_de_caixa, 2)}")

if __name__ == "__main__":
    id_cliente = 85
    mes = date(2025, 3, 1)
    testar_r5_porcentagens(id_cliente, mes)