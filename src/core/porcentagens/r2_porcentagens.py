# src/core/r2_porcentagens.py
from datetime import date
from typing import List, Dict, Any
from sqlalchemy import text
from src.database.db_utils import DatabaseConnection

class R2Porcentagens:
    def __init__(self, id_cliente: int, db_connection: DatabaseConnection):
        self.id_cliente = id_cliente
        self.db = db_connection

    def calcular_porcentagens_lucro_bruto(self, mes: date) -> List[Dict[str, Any]]:
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
            ORDER BY t.valor DESC
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
        
        
    def calcular_porcentagens_despesas_fixas(self, mes: date) -> List[Dict[str, Any]]: # a querie retorna os valores como positivos no final mas no bd é negativo
        query = text("""
            WITH despesas AS (
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
                    AND f.nivel_1 = '5. Despesas Fixas'
                    AND EXTRACT(YEAR FROM f.data) = :year
                    AND EXTRACT(MONTH FROM f.data) = :month
                GROUP BY p.nivel_2
            ),
            total_despesas AS (
                SELECT SUM(valor) AS soma_valores
                FROM despesas
            )
            SELECT 
                d.categoria,
                d.valor,
                CASE 
                    WHEN td.soma_valores = 0 THEN NULL 
                    ELSE (d.valor / td.soma_valores) * 100 
                END AS proporcao
            FROM despesas d
            CROSS JOIN total_despesas td
            ORDER BY d.valor ASC
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
                "valor": abs(float(row["valor"])),
                "proporcao": float(row["proporcao"]) if row["proporcao"] is not None else 0
            }
            for _, row in result.iterrows()
        ] if not result.empty else []
