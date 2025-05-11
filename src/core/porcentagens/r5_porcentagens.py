# src/core/r5_porcentagens.py
from datetime import date
from typing import List, Dict, Any
from sqlalchemy import text
from src.database.db_utils import DatabaseConnection

class R5Porcentagens:
    def __init__(self, id_cliente: int, db_connection: DatabaseConnection):
        """Inicializa a classe R5Porcentagens com ID do cliente e conexão ao banco de dados.

        Args:
            id_cliente: Identificador do cliente.
            db_connection: Conexão com o banco de dados.
        """
        self.id_cliente = id_cliente
        self.db = db_connection

    def calcular_proporcoes_geracao_de_caixa(self, mes: date) -> List[Dict[str, Any]]:
        """Calcula as proporções das categorias da Geração de Caixa em relação ao total.

        Args:
            mes: Data do mês a ser calculado.

        Returns:
            Lista de dicionários com 'categoria', 'valor' e 'proporcao'.
        """
        query = text("""
            WITH
              totais_atual AS (
                SELECT 'Receita' AS categoria, SUM(valor) AS valor
                FROM fc
                WHERE id_cliente = :id_cliente
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '3. Receitas'
                UNION ALL
                SELECT 'Custos Variáveis', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = :id_cliente
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '4. Custos Variáveis'
                UNION ALL
                SELECT 'Despesas Fixas', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = :id_cliente
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '5. Despesas Fixas'
                UNION ALL
                SELECT 'Investimentos', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = :id_cliente
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '6. Investimentos'
                UNION ALL
                SELECT 'Entradas Não Operacionais', SUM(valor)
                FROM fc
                WHERE id_cliente = :id_cliente
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '7.1 Entradas Não Operacionais'
                UNION ALL
                SELECT 'Saídas Não Operacionais', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = :id_cliente
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '7.2 Saídas Não Operacionais'
              ),
              lucro_liquido AS (
                SELECT 
                  'Lucro Líquido' AS categoria,
                  SUM(CASE 
                        WHEN categoria IN ('Receita') THEN valor
                        WHEN categoria IN ('Custos Variáveis', 'Despesas Fixas', 'Investimentos') THEN -valor
                        ELSE 0
                      END) AS valor
                FROM totais_atual
                WHERE categoria IN ('Receita', 'Custos Variáveis', 'Despesas Fixas', 'Investimentos')
              ),
              totais AS (
                SELECT categoria, valor
                FROM lucro_liquido
                UNION ALL
                SELECT categoria, valor
                FROM totais_atual
                WHERE categoria IN ('Entradas Não Operacionais', 'Saídas Não Operacionais')
              ),
              total_geracao_de_caixa AS (
                SELECT SUM(valor) AS soma_valores
                FROM totais
              )
            SELECT 
                t.categoria,
                CASE 
                    WHEN t.categoria = 'Saídas Não Operacionais' THEN ABS(t.valor)
                    ELSE t.valor
                END AS valor,
                CASE 
                    WHEN tgc.soma_valores = 0 THEN 0
                    ELSE (t.valor / tgc.soma_valores) * 100 
                END AS proporcao
            FROM totais t
            CROSS JOIN total_geracao_de_caixa tgc
            ORDER BY t.valor DESC
        """)
        params = {
            "id_cliente": self.id_cliente,
            "year": mes.year,
            "month": mes.month
        }
        try:
            result = self.db.execute_query(query, params)
            return [
                {
                    "categoria": row["categoria"],
                    "valor": float(row["valor"]),
                    "proporcao": round(float(row["proporcao"]), 2)
                }
                for _, row in result.iterrows()
            ] if not result.empty else []
        except Exception as e:
            raise RuntimeError(f"Erro ao calcular proporções da Geração de Caixa: {str(e)}")
