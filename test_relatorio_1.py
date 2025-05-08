from datetime import date
import json
from src.database.db_utils import DatabaseConnection, buscar_clientes
from src.core.indicadores import Indicadores
from src.core.relatorios.relatorio_1 import Relatorio1

def mostrar_relatorio(id_cliente: int, mes_atual: date):
    try:
        # Instanciar conexão com o banco
        db_connection = DatabaseConnection()

        # Buscar nome do cliente dinamicamente
        clientes = buscar_clientes(db_connection)
        cliente = next((c for c in clientes if c['id_cliente'] == id_cliente), None)
        if not cliente:
            raise ValueError(f"Cliente com id_cliente={id_cliente} não encontrado ou não está ativo.")

        nome_cliente = cliente['nome']
        print(f"Gerando relatório para: {nome_cliente} (ID: {id_cliente})")

        # Instanciar Indicadores e Relatorio1
        indicadores = Indicadores(id_cliente, db_connection)
        relatorio = Relatorio1(indicadores, nome_cliente)

        # Executar o método
        resultado = relatorio.gerar_relatorio(mes_atual)

        # Imprimir o dicionário formatado
        print("Saída do relatório:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Erro ao gerar relatório: {str(e)}")

if __name__ == "__main__":
    # Configuração
    id_cliente = 216  # , conforme amostra
    mes_atual = date(2025, 1, 1)  # Março de 2025, conforme amostra
    mostrar_relatorio(id_cliente, mes_atual)