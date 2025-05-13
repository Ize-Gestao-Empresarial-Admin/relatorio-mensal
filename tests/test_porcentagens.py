# test_porcentagens.py
from datetime import date
import json
from src.database.db_utils import DatabaseConnection, buscar_clientes
from src.core.indicadores import Indicadores
from src.core.porcentagens.r1_porcentagens import Porcentagens
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def testar_porcentagens(id_cliente: int, mes: date):
    try:
        db_connection = DatabaseConnection()
        clientes = buscar_clientes(db_connection)
        cliente = next((c for c in clientes if c['id_cliente'] == id_cliente), None)
        if not cliente:
            raise ValueError(f"Cliente com id_cliente={id_cliente} não encontrado ou não está ativo.")

        nome_cliente = cliente['nome']
        logger.info(f"Testando porcentagens para: {nome_cliente} (ID: {id_cliente})")

        indicadores = Indicadores(id_cliente, db_connection)
        porcentagens = Porcentagens(indicadores)

        # Testar Custos Variáveis
        logger.info("Testando porcentagens de Custos Variáveis")
        custos_variaveis = porcentagens.calcular_porcentagens_custos_variaveis(mes)
        print("Custos Variáveis:")
        print(json.dumps(custos_variaveis, indent=2, ensure_ascii=False))

        # Testar Receitas
        logger.info("Testando porcentagens de Receitas")
        receitas = porcentagens.calcular_porcentagens_receitas(mes)
        print("Receitas:")
        print(json.dumps(receitas, indent=2, ensure_ascii=False))

    except Exception as e:
        logger.error(f"Erro ao testar porcentagens: {str(e)}")
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    id_cliente = 85
    mes = date(2025, 3, 1)
    testar_porcentagens(id_cliente, mes)