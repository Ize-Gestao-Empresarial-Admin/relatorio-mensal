# test_relatorio_5.py
from datetime import date
import json
from src.database.db_utils import DatabaseConnection
from src.core.indicadores import Indicadores
from src.core.relatorios.relatorio_5 import Relatorio5

def testar_relatorio(cliente_ids: list, mes: date, display_cliente_nome: str = "Cliente Teste"):
    """
    Testa a geração do Relatório 5 com suporte a múltiplos clientes.

    Args:
        cliente_ids: Lista de IDs dos clientes para consolidação
        mes: Data do mês para geração do relatório
        display_cliente_nome: Nome de exibição para o(s) cliente(s)
    """
    db_connection = DatabaseConnection()
    # Passa a lista de IDs diretamente para Indicadores
    indicadores = Indicadores(cliente_ids, db_connection)
    relatorio = Relatorio5(indicadores, display_cliente_nome)
    
    resultado, notas = relatorio.gerar_relatorio(mes)
    
    # Formatação do resultado para melhor visualização
    print("\n=== Teste Relatório 5 ===")
    print(f"Cliente(s): {display_cliente_nome} (IDs: {cliente_ids})")
    print(f"Período: {mes.strftime('%B/%Y')}")
    print("\nResultado:")
    print(json.dumps({"resultado": resultado, "notas": notas}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # Exemplo de teste com múltiplos clientes
    cliente_ids = [122]  # Você pode adicionar mais IDs conforme necessário
    mes = date(2025, 6, 1)
    nome_exibicao = f"Cliente_{cliente_ids[0]}"
    
    testar_relatorio(cliente_ids, mes, nome_exibicao)