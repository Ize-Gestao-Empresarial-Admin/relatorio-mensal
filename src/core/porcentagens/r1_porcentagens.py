# src/core/r1_porcentagens.py
from datetime import date
from typing import List, Dict, Any
from sqlalchemy import text
from src.database.db_utils import DatabaseConnection

class R1Porcentagens:
    def __init__(self, id_cliente: int, db_connection: DatabaseConnection):
        self.id_cliente = id_cliente
        self.db = db_connection

    def calcular_porcentagens_custos_variaveis(self, mes: date) -> List[Dict[str, Any]]:
        query = text("""
            WITH custos AS (
                SELECT 
                    p.nivel_2 AS categoria,
                    SUM(f.valor) AS valor
                FROM fc f
                JOIN plano_de_contas p
                    ON f.id_cliente = p.id_cliente
                    AND text(f.nivel_3_id) = p.nivel_3_id
                WHERE 
                    f.id_cliente = :id_cliente
                    AND f.visao = 'Realizado'
                    AND f.nivel_1 = '4. Custos Variáveis'
                    AND f.data = :mes
                GROUP BY p.nivel_2
            ),
            total_custos AS (
                SELECT SUM(valor) AS soma_valores
                FROM custos
            )
            SELECT 
                c.categoria,
                c.valor,
                CASE 
                    WHEN tc.soma_valores = 0 THEN NULL 
                    ELSE (c.valor / tc.soma_valores) * 100 
                END AS proporcao
            FROM custos c
            CROSS JOIN total_custos tc
            ORDER BY c.valor ASC
        """)
        params = {
            "id_cliente": self.id_cliente,
            "mes": mes
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

    def calcular_porcentagens_receitas(self, mes: date) -> List[Dict[str, Any]]:
        query = text("""
            WITH receitas AS (
                SELECT 
                    categoria_nivel_3 AS categoria,
                    SUM(f.valor) AS valor
                FROM fc f
                WHERE 
                    f.id_cliente = :id_cliente
                    AND f.visao = 'Realizado'
                    AND f.nivel_1 = '3. Receitas'
                    AND f.data = :mes
                GROUP BY categoria_nivel_3
            ),
            total_receitas AS (
                SELECT SUM(valor) AS soma_valores
                FROM receitas
            )
            SELECT 
                r.categoria,
                r.valor,
                CASE 
                    WHEN tr.soma_valores = 0 THEN NULL 
                    ELSE (r.valor / tr.soma_valores) * 100 
                END AS proporcao
            FROM receitas r
            CROSS JOIN total_receitas tr
            ORDER BY r.valor DESC
        """)
        params = {
            "id_cliente": self.id_cliente,
            "mes": mes
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