# src/core/r4_porcentagens.py
from datetime import date
from typing import List, Dict, Any
from sqlalchemy import text
from src.database.db_utils import DatabaseConnection

class R4Porcentagens:
    def __init__(self, id_cliente: int, db_connection: DatabaseConnection):
        self.id_cliente = id_cliente
        self.db = db_connection

    def calcular_porcentagens_lucro_liquido(self, mes: date) -> List[Dict[str, Any]]:
        query = text("""
            WITH totais AS (
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
            ),
            total_totais AS (
                SELECT SUM(valor) AS soma_valores
                FROM totais
            )
            SELECT 
                t.categoria,
                t.valor,
                CASE 
                    WHEN tt.soma_valores = 0 THEN NULL 
                    ELSE (t.valor / tt.soma_valores) * 100 
                END AS proporcao
            FROM totais t
            CROSS JOIN total_totais tt
            ORDER BY 
                CASE t.categoria
                    WHEN 'Receita' THEN 1
                    WHEN 'Custos Variáveis' THEN 2
                    WHEN 'Despesas Fixas' THEN 3
                    WHEN 'Investimentos' THEN 4
                END
        """)
        params = {
            "id_cliente": self.id_cliente,
            "year": mes.year,
            "month": mes.month
        }
        result = self.db.execute_query(query, params)
        return [
            {
                "categoria": row["categoria"],
                "valor": float(row["valor"]),
                "proporcao": float(row["proporcao"]) if row["proporcao"] is not None else 0
            }
            for _, row in result.iterrows()
        ] if not result.empty else []

    def calcular_porcentagens_entradas_nao_operacionais(self, mes: date) -> List[Dict[str, Any]]:
        query = text("""
            WITH entradas AS (
                SELECT 
                    categoria_nivel_3 AS categoria,
                    SUM(valor) AS valor
                FROM fc
                WHERE 
                    id_cliente = :id_cliente
                    AND visao = 'Realizado'
                    AND EXTRACT(YEAR FROM data) = :year
                    AND EXTRACT(MONTH FROM data) = :month
                    AND nivel_1 = '7.1 Entradas Não Operacionais'
                GROUP BY categoria_nivel_3
            ),
            total_entradas AS (
                SELECT SUM(valor) AS soma_valores
                FROM entradas
            )
            SELECT 
                e.categoria,
                e.valor,
                CASE 
                    WHEN te.soma_valores = 0 THEN NULL 
                    ELSE (e.valor / te.soma_valores) * 100 
                END AS proporcao
            FROM entradas e
            CROSS JOIN total_entradas te
            ORDER BY e.valor DESC
        """)
        params = {
            "id_cliente": self.id_cliente,
            "year": mes.year,
            "month": mes.month
        }
        result = self.db.execute_query(query, params)
        return [
            {
                "categoria": row["categoria"],
                "valor": float(row["valor"]),
                "proporcao": float(row["proporcao"]) if row["proporcao"] is not None else 0
            }
            for _, row in result.iterrows()
        ] if not result.empty else []