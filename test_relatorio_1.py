# test_relatorio_1.py
from datetime import date
from typing import Optional, List, Dict, Any
import json
from dateutil.relativedelta import relativedelta
from src.database.db_utils import DatabaseConnection
from src.core.indicadores import Indicadores
from src.core.relatorios.relatorio_1 import Relatorio1

def testar_relatorio(cliente_ids: list, mes_atual: date, display_cliente_nome: str = "Cliente Teste", mes_anterior: Optional[date] = None):
    """
    Testa a geração do Relatório 1 com suporte a múltiplos clientes.

    Args:
        cliente_ids: Lista de IDs dos clientes para consolidação
        mes_atual: Data do mês atual para geração do relatório
        display_cliente_nome: Nome de exibição para o(s) cliente(s)
        mes_anterior: Data do mês anterior (opcional, calculado automaticamente se não fornecido)
    """
    if mes_anterior is None:
        mes_anterior = mes_atual - relativedelta(months=1)
    
    db_connection = DatabaseConnection()
    # Passa a lista de IDs diretamente para Indicadores
    indicadores = Indicadores(cliente_ids, db_connection)
    relatorio = Relatorio1(indicadores, display_cliente_nome)
    
    resultado = relatorio.gerar_relatorio(mes_atual)
    
    # Formatação do resultado para melhor visualização
    print("\n=== Teste Relatório 1 ===")
    print(f"Cliente(s): {display_cliente_nome} (IDs: {cliente_ids})")
    print(f"Período: {mes_atual.strftime('%B/%Y')}")
    print("\nResultado:")
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # Exemplo de teste com múltiplos clientes
    cliente_ids = [80]  # Você pode adicionar mais IDs conforme necessário
    mes = date(2025, 5, 1)
    nome_exibicao = f"Cliente_{cliente_ids[0]}"
    
    testar_relatorio(cliente_ids, mes, nome_exibicao)
