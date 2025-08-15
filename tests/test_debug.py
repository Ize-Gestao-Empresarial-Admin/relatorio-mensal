# test_debug.py
from datetime import date
import json
from src.database.db_utils import DatabaseConnection
from tests.debug_indicadores import IndicadoresDebug

def testar_debug():
    """Teste de debug para verificar onde estão os zeros."""
    print("=== TESTE DE DEBUG ===")
    
    cliente_ids = [120]
    mes = date(2025, 5, 1)
    
    db_connection = DatabaseConnection()
    indicadores_debug = IndicadoresDebug(cliente_ids, db_connection)
    
    # Teste 1: Função principal de geração de caixa
    print("\n1. Testando calcular_geracao_de_caixa_fc...")
    resultado_principal = indicadores_debug.calcular_geracao_de_caixa_fc(mes)
    
    # Teste 2: Função temporal
    print("\n2. Testando calcular_geracao_de_caixa_temporal_fc...")
    resultado_temporal = indicadores_debug.calcular_geracao_de_caixa_temporal_fc(mes)
    
    print("\n=== RESUMO DOS TESTES ===")
    print(f"Resultado principal: {resultado_principal}")
    print(f"Resultado temporal: {resultado_temporal}")

if __name__ == "__main__":
    testar_debug()