#src/database/db_utils.py
import pandas as pd
from sqlalchemy import create_engine, text
from typing import Optional, Union, Dict, List, Tuple
from datetime import date
from config.settings import DB_CONFIG

class DatabaseConnection:
    def __init__(self):
        self.engine = create_engine(
            f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
            f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
        )

    def execute_query(self, query: Union[str, text], params: Optional[Union[Dict, List, Tuple]] = None) -> pd.DataFrame:
        """Executa uma query SQL e retorna um DataFrame's a DataFrame.

        Args:
            query: Consulta SQL (string ou objeto SQLAlchemy text).
            params: Parâmetros da consulta (dicionário, lista ou tupla).

        Returns:
            DataFrame com os resultados da consulta.

        Raises:
            ValueError: Se a consulta ou parâmetros forem inválidos.
        """
        try:
            return pd.read_sql_query(query, self.engine, params=params)
        except Exception as e:
            raise ValueError(f"Erro ao executar consulta: {str(e)}")

def buscar_clientes(db: DatabaseConnection) -> list:
    """Busca todos os clientes no banco."""
    query = "SELECT nome, id_cliente FROM cliente WHERE ativo = TRUE ORDER BY nome;" # so busca clientes ativos
    df = db.execute_query(query)
    return df.to_dict(orient='records') if not df.empty else []

def obter_meses() -> List[tuple]:
    """Retorna lista de meses."""
    return [
        ("Janeiro", 1), ("Fevereiro", 2), ("Março", 3), ("Abril", 4),
        ("Maio", 5), ("Junho", 6), ("Julho", 7), ("Agosto", 8),
        ("Setembro", 9), ("Outubro", 10), ("Novembro", 11), ("Dezembro", 12)
    ]
    
def obter_anos(db: DatabaseConnection, id_cliente: int) -> List[int]:
    """Retorna uma lista de anos distintos disponíveis na tabela fc para o cliente especificado,
    limitando ao ano atual como máximo.

    Args:
        db: Instância de DatabaseConnection.
        id_cliente: ID do cliente para filtrar os anos.

    Returns:
        Lista de anos ordenada em ordem decrescente, incluindo apenas anos até o atual.
        Se não houver dados, retorna o ano atual.

    Raises:
        ValueError: Se id_cliente for inválido.
    """
    if not isinstance(id_cliente, int) or id_cliente <= 0:
        return [date.today().year]

    query = text("""
        SELECT DISTINCT EXTRACT(YEAR FROM data)::integer AS ano
        FROM fc
        WHERE id_cliente = :id_cliente
        AND EXTRACT(YEAR FROM data) <= :ano_atual
        ORDER BY ano DESC;
    """)
    params = {"id_cliente": id_cliente, "ano_atual": date.today().year}
    df = db.execute_query(query, params)
    anos = df['ano'].tolist() if not df.empty else [date.today().year]
    return anos

