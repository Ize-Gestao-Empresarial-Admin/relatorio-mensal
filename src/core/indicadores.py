# src/core/indicadores.py
from datetime import date
from typing import Union, List, Dict, Any, Optional
from sqlalchemy import text
from src.database.db_utils import DatabaseConnection
import pandas as pd

class Indicadores:
    def __init__(self, id_cliente: Union[int, List[int]], db_connection: DatabaseConnection):
        self.id_cliente = id_cliente
        self.db = db_connection

# Relatório 1 (no relatorio esta inverso, receitas primeiro depois custos variaveis)
    def calcular_custos_variaveis_fc(self, mes: date, categoria_nivel_3: str) -> List[Dict[str, Any]]:
        """Calcula os 5 maiores totais de custos variáveis por nivel_2 em um mês.

        Args:
            mes: Data do mês a ser calculado.
            categoria_nivel_3: Padrão para filtragem (ex.: '4.%', não usado diretamente).

        Returns:
            Lista de dicionários com 'nivel_2', 'total_categoria' (negativo), 'av', e 'ah',
            ordenada por total_categoria ascendente (valores mais negativos primeiro).

        Raises:
            ValueError: Se os parâmetros forem inválidos.
            RuntimeError: Se houver erro na execução da consulta.
        """
        if not isinstance(mes, date):
            raise ValueError("O parâmetro 'mes' deve ser um objeto date.")
        if not isinstance(categoria_nivel_3, str):
            raise ValueError("O parâmetro 'categoria_nivel_3' deve ser uma string.")

        query = text("""
            WITH 
                receita AS (
                    SELECT SUM(valor) AS total_receita
                    FROM fc
                    WHERE id_cliente = ANY (:id_cliente)
                      AND visao = 'Realizado'
                      AND EXTRACT(YEAR FROM data) = :year
                      AND EXTRACT(MONTH FROM data) = :month
                      AND nivel_1 = '3. Receitas'
                ),
                prev_custos AS (
                    SELECT 
                        p.nivel_2 AS categoria,
                        SUM(f.valor) AS prev_valor
                    FROM fc f
                    JOIN plano_de_contas p
                        ON f.id_cliente = p.id_cliente
                        AND text(f.nivel_3_id) = p.nivel_3_id
                    WHERE f.id_cliente = ANY (:id_cliente)
                      AND f.visao = 'Realizado'
                      AND f.nivel_1 = '4. Custos Variáveis'
                      AND f.data < DATE_TRUNC('month', MAKE_DATE(:year, :month, 1))
                      AND f.data >= DATE_TRUNC('month', MAKE_DATE(:year, :month, 1) - INTERVAL '1 month')
                    GROUP BY p.nivel_2
                )
            SELECT 
                p.nivel_2 AS nivel_2,
                SUM(f.valor) AS total_categoria,
                CASE 
                    WHEN r.total_receita = 0 THEN NULL 
                    ELSE SUM(f.valor) / r.total_receita * 100
                END AS av,
                CASE 
                    WHEN prev.prev_valor IS NULL OR prev.prev_valor = 0 THEN NULL 
                    ELSE (SUM(f.valor) / prev.prev_valor - 1) * 100
                END AS ah
            FROM fc f
            JOIN plano_de_contas p
                ON f.id_cliente = p.id_cliente
                AND text(f.nivel_3_id) = p.nivel_3_id
            CROSS JOIN receita r
            LEFT JOIN prev_custos prev 
                ON prev.categoria = p.nivel_2
            WHERE f.id_cliente = ANY (:id_cliente)
                AND f.visao = 'Realizado'
                AND f.nivel_1 = '4. Custos Variáveis'
                AND EXTRACT(YEAR FROM f.data) = :year
                AND EXTRACT(MONTH FROM f.data) = :month
            GROUP BY p.nivel_2, r.total_receita, prev.prev_valor
            ORDER BY total_categoria ASC;
            
        """)

        params = {
            "id_cliente": self.id_cliente,
            "year": mes.year,
            "month": mes.month,
            "prev_year": mes.year if mes.month > 1 else mes.year - 1,
            "prev_month": mes.month - 1 if mes.month > 1 else 12
        }

        try:
            resultado = self.db.execute_query(query, params)
            return [
                {
                    "nivel_2": row["nivel_2"] or "Desconhecido",
                    "total_categoria": float(row["total_categoria"]) if row["total_categoria"] is not None else 0,
                    "av": float(row["av"]) if row["av"] is not None else 0,
                    "ah": float(row["ah"]) if row["ah"] is not None else 0
                }
                for _, row in resultado.iterrows()
            ] if not resultado.empty else []
        except Exception as e:
            raise RuntimeError(f"Erro ao calcular custos variáveis: {str(e)}")

    def calcular_receitas_fc(self, mes: date, categoria_nivel_3: str) -> List[Dict[str, Any]]:
        """Calcula os 5 maiores totais de receitas por categoria_nivel_3 em um mês.

        Args:
            mes: Data do mês a ser calculado.
            categoria_nivel_3: Padrão para filtragem (ex.: '3.%', não usado diretamente).

        Returns:
            Lista de dicionários com 'categoria_nivel_3', 'total_categoria' (positivo), 'av', e 'ah',
            ordenada por total_categoria decrescente.

        Raises:
            ValueError: Se os parâmetros forem inválidos.
            RuntimeError: Se houver erro na execução da consulta.
        """
        if not isinstance(mes, date):
            raise ValueError("O parâmetro 'mes' deve ser um objeto date.")
        if not isinstance(categoria_nivel_3, str):
            raise ValueError("O parâmetro 'categoria_nivel_3' deve ser uma string.")

        query = text("""
            WITH 
              receita_atual AS (
                SELECT SUM(valor) AS total
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '3. Receitas'
              ),
              receita_anterior AS (
                SELECT 
                  categoria_nivel_3,
                  SUM(valor) AS total_prev
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :prev_year
                  AND EXTRACT(MONTH FROM data) = :prev_month
                  AND nivel_1 = '3. Receitas'
                GROUP BY categoria_nivel_3
              )
            SELECT
              f.categoria_nivel_3 AS categoria_nivel_3,
              SUM(f.valor) AS total_categoria,
              CASE 
                WHEN ra.total = 0 THEN NULL 
                ELSE SUM(f.valor) / ra.total * 100
              END AS av,
              CASE 
                WHEN rp.total_prev IS NULL OR rp.total_prev = 0 THEN NULL
                ELSE (SUM(f.valor) / rp.total_prev - 1) * 100
              END AS ah
            FROM fc f
            CROSS JOIN receita_atual ra
            LEFT JOIN receita_anterior rp 
              ON rp.categoria_nivel_3 = f.categoria_nivel_3
            WHERE f.id_cliente = ANY (:id_cliente)
              AND f.visao = 'Realizado'
              AND EXTRACT(YEAR FROM f.data) = :year
              AND EXTRACT(MONTH FROM f.data) = :month
              AND f.nivel_1 = '3. Receitas'
            GROUP BY f.categoria_nivel_3, ra.total, rp.total_prev
            ORDER BY total_categoria DESC;
        """)

        params = {
            "id_cliente": self.id_cliente,
            "year": mes.year,
            "month": mes.month,
            "prev_year": mes.year if mes.month > 1 else mes.year - 1,
            "prev_month": mes.month - 1 if mes.month > 1 else 12
        }

        try:
            resultado = self.db.execute_query(query, params)
            return [
                {
                    "categoria_nivel_3": row["categoria_nivel_3"],
                    "total_categoria": float(row["total_categoria"]) if row["total_categoria"] is not None else 0,
                    "av": float(row["av"]) if row["av"] is not None else 0,
                    "ah": float(row["ah"]) if row["ah"] is not None else 0
                }
                for _, row in resultado.iterrows()
            ] if not resultado.empty else []
        except Exception as e:
            raise RuntimeError(f"Erro ao calcular receitas: {str(e)}")
            
# Relatorio 2
    def calcular_lucro_bruto_fc(self, mes: date) -> List[Dict[str, Any]]:
        """Calcula as categorias de Lucro Bruto (Receitas e Custos Variáveis) do fluxo de caixa (fc) com AV e AH.

        Args:
            mes: Data do mês a ser calculado.

        Returns:
            Lista de dicionários com 'categoria', 'valor', 'av' (análise vertical), e 'ah' (análise horizontal).
        """
        query = text("""
            WITH
              totais_atual AS (
                SELECT 'Receita' AS categoria, SUM(valor) AS valor
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '3. Receitas'
                UNION ALL
                SELECT 'Custos Variáveis', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '4. Custos Variáveis'
              ),
              totais_anterior AS (
                SELECT 'Receita' AS categoria, SUM(valor) AS prev_valor
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :prev_year
                  AND EXTRACT(MONTH FROM data) = :prev_month
                  AND nivel_1 = '3. Receitas'
                UNION ALL
                SELECT 'Custos Variáveis', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :prev_year
                  AND EXTRACT(MONTH FROM data) = :prev_month
                  AND nivel_1 = '4. Custos Variáveis'
              ),
              receita_total AS (
                SELECT valor AS total
                FROM totais_atual
                WHERE categoria = 'Receita'
              )
            SELECT
              a.categoria,
              a.valor,
              CASE
                WHEN rt.total = 0 THEN NULL
                ELSE a.valor / rt.total * 100
              END AS av,
              CASE
                WHEN p.prev_valor IS NULL OR p.prev_valor = 0 THEN NULL
                ELSE (a.valor / p.prev_valor - 1) * 100
              END AS ah
            FROM totais_atual a
            CROSS JOIN receita_total rt
            LEFT JOIN totais_anterior p
              ON p.categoria = a.categoria
            ORDER BY 
              CASE a.categoria
                WHEN 'Receita' THEN 1
                WHEN 'Custos Variáveis' THEN 2
              END;
        """)
        params = {
            "id_cliente": self.id_cliente,
            "year": mes.year,
            "month": mes.month,
            "prev_year": mes.year if mes.month > 1 else mes.year - 1,
            "prev_month": mes.month - 1 if mes.month > 1 else 12
        }
        try:
            result = self.db.execute_query(query, params)
            return [
                {
                    "categoria": row["categoria"],
                    "valor": float(row["valor"]) if row["valor"] is not None else 0,
                    "av": float(row["av"]) if row["av"] is not None else 0,
                    "ah": float(row["ah"]) if row["ah"] is not None else 0
                }
                for _, row in result.iterrows()
            ] if not result.empty else []
        except Exception as e:
            raise RuntimeError(f"Erro ao calcular lucro bruto: {str(e)}")

    def calcular_despesas_fixas_fc(self, mes: date) -> List[Dict[str, Any]]:
        """Calcula as despesas fixas do fluxo de caixa (fc) por categoria nivel_2 com AV e AH.

        Args:
            mes: Data do mês a ser calculado.

        Returns:
            Lista de dicionários com 'categoria', 'valor', 'av' (análise vertical), e 'ah' (análise horizontal).
        """
        query = text("""
            WITH 
              receita AS (
                SELECT SUM(valor) AS total_receita
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '3. Receitas'
              ),
              prev_despesas AS (
                SELECT 
                  p.nivel_2 AS categoria_nivel_2,
                  SUM(f.valor) AS prev_valor
                FROM fc f
                JOIN plano_de_contas p
                  ON f.id_cliente = p.id_cliente
                  AND text(f.nivel_3_id) = p.nivel_3_id
                WHERE f.id_cliente = ANY (:id_cliente)
                  AND f.visao = 'Realizado'
                  AND f.nivel_1 = '5. Despesas Fixas'
                  AND EXTRACT(YEAR FROM f.data) = :prev_year
                  AND EXTRACT(MONTH FROM f.data) = :prev_month
                GROUP BY p.nivel_2
              )
            SELECT 
              p.nivel_2 AS categoria_nivel_2,
              SUM(f.valor) AS total_valor,
              CASE 
                WHEN r.total_receita = 0 THEN NULL 
                ELSE SUM(f.valor) / r.total_receita * 100
              END AS av,
              CASE 
                WHEN prev.prev_valor IS NULL OR prev.prev_valor = 0 THEN NULL 
                ELSE (SUM(f.valor) / prev.prev_valor - 1) * 100
              END AS ah
            FROM fc f
            JOIN plano_de_contas p
              ON f.id_cliente = p.id_cliente
              AND text(f.nivel_3_id) = p.nivel_3_id
            CROSS JOIN receita r
            LEFT JOIN prev_despesas prev 
              ON prev.categoria_nivel_2 = p.nivel_2
            WHERE f.id_cliente = ANY (:id_cliente)
              AND f.visao = 'Realizado'
              AND f.nivel_1 = '5. Despesas Fixas'
              AND EXTRACT(YEAR FROM f.data) = :year
              AND EXTRACT(MONTH FROM f.data) = :month
            GROUP BY p.nivel_2, r.total_receita, prev.prev_valor
            ORDER BY total_valor ASC;
        """)
        params = {
            "id_cliente": self.id_cliente,
            "year": mes.year,
            "month": mes.month,
            "prev_year": mes.year if mes.month > 1 else mes.year - 1,
            "prev_month": mes.month - 1 if mes.month > 1 else 12
        }
        try:
            result = self.db.execute_query(query, params)
            return [
                {
                    "categoria": row["categoria_nivel_2"],
                    "valor": float(row["total_valor"]) if row["total_valor"] is not None else 0,
                    "av": float(row["av"]) if row["av"] is not None else 0,
                    "ah": float(row["ah"]) if row["ah"] is not None else 0
                }
                for _, row in result.iterrows()
            ] if not result.empty else []
        except Exception as e:
            raise RuntimeError(f"Erro ao calcular despesas fixas: {str(e)}")
        
#Relatorio 3
    def calcular_lucro_operacional_fc(self, mes_atual: date, mes_anterior: Optional[date] = None) -> List[Dict[str, Any]]:
        """Calcula Receita, Custos Variáveis, Despesas Fixas, AV e AH para o Lucro Operacional."""
        query = text("""
            WITH
              totais_atual AS (
                SELECT 'Receita' AS categoria, SUM(valor) AS valor
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :ano_atual
                  AND EXTRACT(MONTH FROM data) = :mes_atual
                  AND nivel_1 = '3. Receitas'
                UNION ALL
                SELECT 'Custos Variáveis', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :ano_atual
                  AND EXTRACT(MONTH FROM data) = :mes_atual
                  AND nivel_1 = '4. Custos Variáveis'
                UNION ALL
                SELECT 'Despesas Fixas', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :ano_atual
                  AND EXTRACT(MONTH FROM data) = :mes_atual
                  AND nivel_1 = '5. Despesas Fixas'
              ),
              totais_anterior AS (
                SELECT 'Receita' AS categoria, SUM(valor) AS prev_valor
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :ano_anterior
                  AND EXTRACT(MONTH FROM data) = :mes_anterior
                  AND nivel_1 = '3. Receitas'
                UNION ALL
                SELECT 'Custos Variáveis', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :ano_anterior
                  AND EXTRACT(MONTH FROM data) = :mes_anterior
                  AND nivel_1 = '4. Custos Variáveis'
                UNION ALL
                SELECT 'Despesas Fixas', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :ano_anterior
                  AND EXTRACT(MONTH FROM data) = :mes_anterior
                  AND nivel_1 = '5. Despesas Fixas'
              ),
              receita_total AS (
                SELECT valor AS total
                FROM totais_atual
                WHERE categoria = 'Receita'
              )
            SELECT
              a.categoria,
              a.valor,
              CASE
                WHEN rt.total = 0 THEN NULL
                ELSE a.valor / rt.total * 100
              END AS av,
              CASE
                WHEN p.prev_valor IS NULL OR p.prev_valor = 0 THEN NULL
                ELSE (a.valor / p.prev_valor - 1) * 100
              END AS ah
            FROM totais_atual a
            CROSS JOIN receita_total rt
            LEFT JOIN totais_anterior p
              ON p.categoria = a.categoria
            ORDER BY 
              CASE a.categoria
                WHEN 'Receita' THEN 1
                WHEN 'Custos Variáveis' THEN 2
                WHEN 'Despesas Fixas' THEN 3
              END;
        """)
        params = {
            "id_cliente": self.id_cliente,
            "ano_atual": mes_atual.year,
            "mes_atual": mes_atual.month,
            "ano_anterior": mes_anterior.year if mes_anterior else mes_atual.year,
            "mes_anterior": mes_anterior.month if mes_anterior else mes_atual.month
        }
        result = self.db.execute_query(query, params)
        return result.to_dict('records') # type: ignore

    def calcular_investimentos_fc(self, mes_atual: date, mes_anterior: Optional[date] = None) -> List[Dict[str, Any]]:
          """Calcula categorias de Investimentos (nivel_2 6.1, 6.2, 6.3), com AV e AH."""
          query = text("""
              WITH 
                receita AS (
                  SELECT SUM(valor) AS total_receita
                  FROM fc
                  WHERE id_cliente = ANY (:id_cliente)
                    AND visao = 'Realizado'
                    AND EXTRACT(YEAR FROM data) = :ano_atual
                    AND EXTRACT(MONTH FROM data) = :mes_atual
                    AND nivel_1 = '3. Receitas'
                ),
                prev_custos AS (
                  SELECT 
                    p.nivel_2 AS categoria,
                    SUM(f.valor) AS prev_valor
                  FROM fc f
                  JOIN plano_de_contas p
                    ON f.id_cliente = p.id_cliente
                    AND text(f.nivel_3_id) = p.nivel_3_id
                  WHERE f.id_cliente = ANY (:id_cliente)
                    AND f.visao = 'Realizado'
                    AND f.nivel_1 = '6. Investimentos'
                    AND EXTRACT(YEAR FROM f.data) = :ano_anterior
                    AND EXTRACT(MONTH FROM f.data) = :mes_anterior
                    AND p.nivel_2 LIKE 
                      '6.%'
                  GROUP BY p.nivel_2
                )
              SELECT 
                p.nivel_2 AS categoria,
                SUM(f.valor) AS valor,
                CASE 
                  WHEN r.total_receita = 0 THEN NULL 
                  ELSE SUM(f.valor) / r.total_receita * 100
                END AS av,
                CASE 
                  WHEN prev.prev_valor IS NULL OR prev.prev_valor = 0 THEN NULL 
                  ELSE (SUM(f.valor) / prev.prev_valor - 1) * 100
                END AS ah
              FROM fc f
              JOIN plano_de_contas p
                ON f.id_cliente = p.id_cliente
                AND text(f.nivel_3_id) = p.nivel_3_id
              CROSS JOIN receita r
              LEFT JOIN prev_custos prev 
                ON prev.categoria = p.nivel_2
              WHERE f.id_cliente = ANY (:id_cliente)
                AND f.visao = 'Realizado'
                AND f.nivel_1 = '6. Investimentos'
                AND EXTRACT(YEAR FROM f.data) = :ano_atual
                AND EXTRACT(MONTH FROM f.data) = :mes_atual
                AND p.nivel_2 LIKE '6.%' 
              GROUP BY p.nivel_2, r.total_receita, prev.prev_valor
              ORDER BY valor DESC;
          """)
          params = {
              "id_cliente": self.id_cliente,
              "ano_atual": mes_atual.year,
              "mes_atual": mes_atual.month,
              "ano_anterior": mes_anterior.year if mes_anterior else mes_atual.year,
              "mes_anterior": mes_anterior.month if mes_anterior else mes_atual.month
          }
          result = self.db.execute_query(query, params)
          return result.to_dict('records') # type: ignore
        
  # Relatorio 4      
    def calcular_lucro_liquido_fc(self, mes: date) -> List[Dict[str, Any]]:
      """Calcula as categorias que compõem o Lucro Líquido (Receita, Custos Variáveis, Despesas Fixas, Investimentos) do fluxo de caixa (fc).

      Args:
          mes: Data do mês a ser calculado.

      Returns:
          Lista de dicionários com 'categoria', 'valor', 'av' (análise vertical), e 'ah' (análise horizontal).
      """
      query = text("""
          WITH
            totais_atual AS (
              SELECT 'Receita' AS categoria, SUM(valor) AS valor
              FROM fc
              WHERE id_cliente = ANY (:id_cliente)
                AND visao = 'Realizado'
                AND EXTRACT(YEAR FROM data) = :year
                AND EXTRACT(MONTH FROM data) = :month
                AND nivel_1 = '3. Receitas'
              UNION ALL
              SELECT 'Custos Variáveis', SUM(valor) * -1
              FROM fc
              WHERE id_cliente = ANY (:id_cliente)
                AND visao = 'Realizado'
                AND EXTRACT(YEAR FROM data) = :year
                AND EXTRACT(MONTH FROM data) = :month
                AND nivel_1 = '4. Custos Variáveis'
              UNION ALL
              SELECT 'Despesas Fixas', SUM(valor) * -1
              FROM fc
              WHERE id_cliente = ANY (:id_cliente)
                AND visao = 'Realizado'
                AND EXTRACT(YEAR FROM data) = :year
                AND EXTRACT(MONTH FROM data) = :month
                AND nivel_1 = '5. Despesas Fixas'
              UNION ALL
              SELECT 'Investimentos', SUM(valor) * -1
              FROM fc
              WHERE id_cliente = ANY (:id_cliente)
                AND visao = 'Realizado'
                AND EXTRACT(YEAR FROM data) = :year
                AND EXTRACT(MONTH FROM data) = :month
                AND nivel_1 = '6. Investimentos'
            ),
            totais_anterior AS (
              SELECT 'Receita' AS categoria, SUM(valor) AS prev_valor
              FROM fc
              WHERE id_cliente = ANY (:id_cliente)
                AND visao = 'Realizado'
                AND EXTRACT(YEAR FROM data) = :prev_year
                AND EXTRACT(MONTH FROM data) = :prev_month
                AND nivel_1 = '3. Receitas'
              UNION ALL
              SELECT 'Custos Variáveis', SUM(valor) * -1
              FROM fc
              WHERE id_cliente = ANY (:id_cliente)
                AND visao = 'Realizado'
                AND EXTRACT(YEAR FROM data) = :prev_year
                AND EXTRACT(MONTH FROM data) = :prev_month
                AND nivel_1 = '4. Custos Variáveis'
              UNION ALL
              SELECT 'Despesas Fixas', SUM(valor) * -1
              FROM fc
              WHERE id_cliente = ANY (:id_cliente)
                AND visao = 'Realizado'
                AND EXTRACT(YEAR FROM data) = :prev_year
                AND EXTRACT(MONTH FROM data) = :prev_month
                AND nivel_1 = '5. Despesas Fixas'
              UNION ALL
              SELECT 'Investimentos', SUM(valor) * -1
              FROM fc
              WHERE id_cliente = ANY (:id_cliente)
                AND visao = 'Realizado'
                AND EXTRACT(YEAR FROM data) = :prev_year
                AND EXTRACT(MONTH FROM data) = :prev_month
                AND nivel_1 = '6. Investimentos'
            ),
            receita_total AS (
              SELECT valor AS total
              FROM totais_atual
              WHERE categoria = 'Receita'
            )
          SELECT
            a.categoria,
            a.valor,
            CASE
              WHEN rt.total = 0 THEN NULL
              ELSE a.valor / rt.total * 100
            END AS av,
            CASE
              WHEN p.prev_valor IS NULL OR p.prev_valor = 0 THEN NULL
              ELSE (a.valor / p.prev_valor - 1) * 100
            END AS ah
          FROM totais_atual a
          CROSS JOIN receita_total rt
          LEFT JOIN totais_anterior p
            ON p.categoria = a.categoria
          ORDER BY 
            CASE a.categoria
              WHEN 'Receita' THEN 1
              WHEN 'Custos Variáveis' THEN 2
              WHEN 'Despesas Fixas' THEN 3
              WHEN 'Investimentos' THEN 4
            END;
      """)
      params = {
          "id_cliente": self.id_cliente,
          "year": mes.year,
          "month": mes.month,
          "prev_year": mes.year if mes.month > 1 else mes.year - 1,
          "prev_month": mes.month - 1 if mes.month > 1 else 12
      }
      try:
          result = self.db.execute_query(query, params)
          return [
              {
                  "categoria": row["categoria"],
                  "valor": float(row["valor"]) if row["valor"] is not None else 0,
                  "av": float(row["av"]) if row["av"] is not None else 0,
                  "ah": float(row["ah"]) if row["ah"] is not None else 0
              }
              for _, row in result.iterrows()
          ] if not result.empty else []
      except Exception as e:
          raise RuntimeError(f"Erro ao calcular lucro líquido: {str(e)}")

    def calcular_entradas_nao_operacionais_fc(self, mes: date) -> List[Dict[str, Any]]:
        """Calcula as Entradas Não Operacionais do fluxo de caixa (fc) por categoria_nivel_3 com AV e AH.

        Args:
            mes: Data do mês a ser calculado.

        Returns:
            Lista de dicionários com 'categoria_nivel_3', 'total_valor', 'av', e 'ah'.
        """
        query = text("""
            WITH 
              receita_total AS (
                SELECT 
                  SUM(valor) AS total_receita
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND LOWER(TRIM(nivel_1)) = LOWER('3. Receitas')
              ),
              prev_entradas AS (
                SELECT 
                  LOWER(TRIM(categoria_nivel_3)) AS categoria_nivel_3,
                  SUM(valor) AS prev_valor
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :prev_year
                  AND EXTRACT(MONTH FROM data) = :prev_month
                  AND LOWER(TRIM(nivel_1)) IN (
                    LOWER('7.1 Entradas Não Operacionais')
                  )
                GROUP BY LOWER(TRIM(categoria_nivel_3))
              ),
              current_entradas AS (
                SELECT 
                  LOWER(TRIM(categoria_nivel_3)) AS categoria_nivel_3,
                  SUM(valor) AS total_valor
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND LOWER(TRIM(nivel_1)) IN (
                    LOWER('7.1 Entradas Não Operacionais')
                  )
                GROUP BY LOWER(TRIM(categoria_nivel_3))
              )
            SELECT
              c.categoria_nivel_3 AS categoria_nivel_3,
              c.total_valor,
              CASE 
                WHEN rt.total_receita = 0 THEN NULL 
                ELSE c.total_valor / rt.total_receita * 100
              END AS av,
              CASE 
                WHEN p.prev_valor IS NULL OR p.prev_valor = 0 THEN NULL 
                ELSE (c.total_valor / p.prev_valor - 1) * 100
              END AS ah
            FROM current_entradas c
            CROSS JOIN receita_total rt
            LEFT JOIN prev_entradas p 
              ON p.categoria_nivel_3 = c.categoria_nivel_3
            ORDER BY c.total_valor DESC;
        """)
        params = {
            "id_cliente": self.id_cliente,
            "year": mes.year,
            "month": mes.month,
            "prev_year": mes.year if mes.month > 1 else mes.year - 1,
            "prev_month": mes.month - 1 if mes.month > 1 else 12
        }
        try:
            result = self.db.execute_query(query, params)
            return [
                {
                    "categoria_nivel_3": row["categoria_nivel_3"],
                    "total_valor": float(row["total_valor"]) if row["total_valor"] is not None else 0,
                    "av": float(row["av"]) if row["av"] is not None else 0,
                    "ah": float(row["ah"]) if row["ah"] is not None else 0
                }
                for _, row in result.iterrows()
            ] if not result.empty else []
        except Exception as e:
            raise RuntimeError(f"Erro ao calcular entradas não operacionais: {str(e)}")
          
# Relatorio 5
    def calcular_saidas_nao_operacionais_fc(self, mes: date) -> List[Dict[str, Any]]:
        """Calcula o total de Saídas Não Operacionais do fluxo de caixa (fc).

        Args:
            mes: Data do mês a ser calculado.

        Returns:
            Lista com um dicionário contendo 'categoria' e 'valor'.
        """
        query = text("""
            SELECT
                'Saídas Não Operacionais' AS categoria,
                SUM(valor) AS total_valor
            FROM fc
            WHERE id_cliente = ANY (:id_cliente)
              AND visao = 'Realizado'
              AND EXTRACT(YEAR FROM data) = :year
              AND EXTRACT(MONTH FROM data) = :month
              AND LOWER(TRIM(nivel_1)) = LOWER('7.2 Saídas Não Operacionais');
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
                    "valor": float(row["total_valor"]) if row["total_valor"] is not None else 0  # Ajustado para total_valor
                }
                for _, row in result.iterrows()
            ] if not result.empty else [{"categoria": "Saídas Não Operacionais", "valor": 0.0}]
        except Exception as e:
            raise RuntimeError(f"Erro ao calcular saídas não operacionais: {str(e)}")
          
    def calcular_resultados_nao_operacionais_fc(self, mes: date) -> List[Dict[str, Any]]:
      """Calcula o Resultado Não Operacional (Entradas - Saídas) do fluxo de caixa por nivel_1 com AV e AH.

      Args:
          mes: Data do mês a ser calculado.

      Returns:
          Lista de dicionários com 'nivel_1', 'total_valor', 'av' e 'ah'.
      """
      query = text("""
          WITH 
            receita_total AS (
              SELECT 
                SUM(valor) AS total_receita
              FROM fc
              WHERE id_cliente = ANY (:id_cliente)
                AND visao = 'Realizado'
                AND EXTRACT(YEAR FROM data) = :year
                AND EXTRACT(MONTH FROM data) = :month
                AND LOWER(TRIM(nivel_1)) = LOWER('3. Receitas')
            ),
            prev_resultado AS (
              SELECT 
                nivel_1,
                SUM(valor) AS prev_valor
              FROM fc
              WHERE id_cliente = ANY (:id_cliente)
                AND visao = 'Realizado'
                AND EXTRACT(YEAR FROM data) = :prev_year
                AND EXTRACT(MONTH FROM data) = :prev_month
                AND LOWER(TRIM(nivel_1)) IN (
                  LOWER('7.1 Entradas Não Operacionais'),
                  LOWER('7.2 Saídas Não Operacionais')
                )
              GROUP BY nivel_1
            ),
            current_resultado AS (
              SELECT 
                nivel_1,
                SUM(valor) AS total_valor
              FROM fc
              WHERE id_cliente = ANY (:id_cliente)
                AND visao = 'Realizado'
                AND EXTRACT(YEAR FROM data) = :year
                AND EXTRACT(MONTH FROM data) = :month
                AND LOWER(TRIM(nivel_1)) IN (
                  LOWER('7.1 Entradas Não Operacionais'),
                  LOWER('7.2 Saídas Não Operacionais')
                )
              GROUP BY nivel_1
            )
          SELECT
            c.nivel_1 AS nivel_1,
            c.total_valor,
            CASE 
              WHEN rt.total_receita = 0 THEN NULL 
              ELSE c.total_valor / rt.total_receita * 100
            END AS av,
            CASE 
              WHEN p.prev_valor IS NULL OR p.prev_valor = 0 THEN NULL 
              ELSE (c.total_valor / p.prev_valor - 1) * 100
            END AS ah
          FROM current_resultado c
          CROSS JOIN receita_total rt
          LEFT JOIN prev_resultado p 
            ON p.nivel_1 = c.nivel_1
          ORDER BY c.total_valor DESC;
      """)
      params = {
          "id_cliente": self.id_cliente,
          "year": mes.year,
          "month": mes.month,
          "prev_year": mes.year if mes.month > 1 else mes.year - 1,
          "prev_month": mes.month - 1 if mes.month > 1 else 12
      }
      try:
          result = self.db.execute_query(query, params)
          return [
              {
                  "nivel_1": row["nivel_1"],
                  "total_valor": float(row["total_valor"]) if row["total_valor"] is not None else 0,
                  "av": float(row["av"]) if row["av"] is not None else 0,
                  "ah": float(row["ah"]) if row["ah"] is not None else 0
              }
              for _, row in result.iterrows()
          ] if not result.empty else []
      except Exception as e:
          raise RuntimeError(f"Erro ao calcular resultado não operacional: {str(e)}")


    def calcular_geracao_de_caixa_fc(self, mes: date) -> List[Dict[str, Any]]:
        """Calcula as categorias que compõem a Geração de Caixa do fluxo de caixa (fc).

        Args:
            mes: Data do mês a ser calculado.

        Returns:
            Lista de dicionários com 'categoria', 'valor', 'av' (análise vertical), e 'ah' (análise horizontal).
        """
        query = text("""
            WITH
              totais_atual AS (
                SELECT 'Receita' AS categoria, SUM(valor) AS valor
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '3. Receitas'
                UNION ALL
                SELECT 'Custos Variáveis', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '4. Custos Variáveis'
                UNION ALL
                SELECT 'Despesas Fixas', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '5. Despesas Fixas'
                UNION ALL
                SELECT 'Investimentos', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '6. Investimentos'
                UNION ALL
                SELECT 'Entradas Não Operacionais', SUM(valor)
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '7.1 Entradas Não Operacionais'
                UNION ALL
                SELECT 'Saídas Não Operacionais', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :year
                  AND EXTRACT(MONTH FROM data) = :month
                  AND nivel_1 = '7.2 Saídas Não Operacionais'
              ),
              totais_anterior AS (
                SELECT 'Receita' AS categoria, SUM(valor) AS prev_valor
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :prev_year
                  AND EXTRACT(MONTH FROM data) = :prev_month
                  AND nivel_1 = '3. Receitas'
                UNION ALL
                SELECT 'Custos Variáveis', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :prev_year
                  AND EXTRACT(MONTH FROM data) = :prev_month
                  AND nivel_1 = '4. Custos Variáveis'
                UNION ALL
                SELECT 'Despesas Fixas', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :prev_year
                  AND EXTRACT(MONTH FROM data) = :prev_month
                  AND nivel_1 = '5. Despesas Fixas'
                UNION ALL
                SELECT 'Investimentos', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :prev_year
                  AND EXTRACT(MONTH FROM data) = :prev_month
                  AND nivel_1 = '6. Investimentos'
                UNION ALL
                SELECT 'Entradas Não Operacionais', SUM(valor)
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :prev_year
                  AND EXTRACT(MONTH FROM data) = :prev_month
                  AND nivel_1 = '7.1 Entradas Não Operacionais'
                UNION ALL
                SELECT 'Saídas Não Operacionais', SUM(valor) * -1
                FROM fc
                WHERE id_cliente = ANY (:id_cliente)
                  AND visao = 'Realizado'
                  AND EXTRACT(YEAR FROM data) = :prev_year
                  AND EXTRACT(MONTH FROM data) = :prev_month
                  AND nivel_1 = '7.2 Saídas Não Operacionais'
              ),
              receita_total AS (
                SELECT valor AS total
                FROM totais_atual
                WHERE categoria = 'Receita'
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
              lucro_liquido_prev AS (
                SELECT 
                  'Lucro Líquido' AS categoria,
                  SUM(CASE 
                        WHEN categoria IN ('Receita') THEN prev_valor
                        WHEN categoria IN ('Custos Variáveis', 'Despesas Fixas', 'Investimentos') THEN -prev_valor
                        ELSE 0
                      END) AS prev_valor
                FROM totais_anterior
                WHERE categoria IN ('Receita', 'Custos Variáveis', 'Despesas Fixas', 'Investimentos')
              ),
              final AS (
                SELECT 
                  l.categoria,
                  l.valor,
                  CASE
                    WHEN rt.total = 0 THEN NULL
                    ELSE l.valor / rt.total * 100
                  END AS av,
                  CASE
                    WHEN lp.prev_valor IS NULL OR lp.prev_valor = 0 THEN NULL
                    WHEN lp.prev_valor < 0 AND l.valor > 0 THEN 
                      ((l.valor - lp.prev_valor) / ABS(lp.prev_valor)) * 100  -- Ajuste para quando o anterior é negativo
                    ELSE 
                      (l.valor / lp.prev_valor - 1) * 100
                  END AS ah
                FROM lucro_liquido l
                CROSS JOIN receita_total rt
                LEFT JOIN lucro_liquido_prev lp
                  ON lp.categoria = l.categoria
                UNION ALL
                SELECT 
                  a.categoria,
                  a.valor,
                  CASE
                    WHEN rt.total = 0 THEN NULL
                    ELSE a.valor / rt.total * 100
                  END AS av,
                  CASE
                    WHEN p.prev_valor IS NULL OR p.prev_valor = 0 THEN NULL
                    ELSE (a.valor / p.prev_valor - 1) * 100
                  END AS ah
                FROM totais_atual a
                CROSS JOIN receita_total rt
                LEFT JOIN totais_anterior p
                  ON p.categoria = a.categoria
                WHERE a.categoria IN ('Entradas Não Operacionais', 'Saídas Não Operacionais')
              )
            SELECT
              categoria,
              valor,
              av,
              ah
            FROM final
            ORDER BY 
              CASE categoria
                WHEN 'Lucro Líquido' THEN 1
                WHEN 'Entradas Não Operacionais' THEN 2
                WHEN 'Saídas Não Operacionais' THEN 3
              END;
        """)
        params = {
            "id_cliente": self.id_cliente,
            "year": mes.year,
            "month": mes.month,
            "prev_year": mes.year if mes.month > 1 else mes.year - 1,
            "prev_month": mes.month - 1 if mes.month > 1 else 12
        }
        try:
            result = self.db.execute_query(query, params)
            return [
                {
                    "categoria": row["categoria"],
                    "valor": float(row["valor"]) if row["valor"] is not None else 0,
                    "av": float(row["av"]) if row["av"] is not None else 0,
                    "ah": float(row["ah"]) if row["ah"] is not None else 0
                }
                for _, row in result.iterrows()
            ] if not result.empty else []
        except Exception as e:
            raise RuntimeError(f"Erro ao calcular geração de caixa: {str(e)}")

    def calcular_geracao_de_caixa_temporal_fc(self, mes_atual: date) -> List[Dict[str, Any]]:
        """Calcula a Geração de Caixa dos últimos 3 meses e a análise horizontal (ah) em relação ao mês anterior.

        Args:
            mes_atual: Data do mês atual a ser considerado (o intervalo será mes_atual e os 2 meses anteriores).

        Returns:
            Lista de dicionários com 'mes', 'valor' (Geração de Caixa), e 'ah' (análise horizontal).
        """
        # Definir os 3 meses a serem calculados
        meses = []
        for i in range(3):
            ano = mes_atual.year if mes_atual.month > i else mes_atual.year - 1
            mes = mes_atual.month - i if mes_atual.month > i else 12 - (i - mes_atual.month)
            meses.append(date(ano, mes, 1))

        # Calcular a Geração de Caixa para cada mês (e o mês anterior ao primeiro)
        resultados_por_mes = []
        for i, mes in enumerate(meses):
            # Calcular a Geração de Caixa do mês atual
            geracao_de_caixa = self.calcular_geracao_de_caixa_fc(mes)
            
            # CORREÇÃO: Usar safe_float para lidar com valores NaN que estavam quebrando o cálculo
            from src.core.utils import safe_float
            total = sum(
                safe_float(r.get("valor", 0)) if r.get("categoria") != "Saídas Não Operacionais" 
                else -safe_float(r.get("valor", 0))
                for r in geracao_de_caixa
            )

            # Calcular o valor do mês anterior para o ah
            mes_anterior = date(mes.year if mes.month > 1 else mes.year - 1,
                             mes.month - 1 if mes.month > 1 else 12, 1)
            geracao_de_caixa_anterior = self.calcular_geracao_de_caixa_fc(mes_anterior)
            
            # CORREÇÃO: Também usar safe_float aqui
            total_anterior = sum(
                safe_float(r.get("valor", 0)) if r.get("categoria") != "Saídas Não Operacionais" 
                else -safe_float(r.get("valor", 0))
                for r in geracao_de_caixa_anterior
            )

            # Calcular o ah com a nova lógica: variação percentual baseada no módulo
            if total_anterior == 0:
                ah = 0  # Caso especial: mês anterior zero ou infinito
            else:
                valor_abs_atual = abs(total)
                valor_abs_anterior = abs(total_anterior)
                ah = ((valor_abs_atual - valor_abs_anterior) / valor_abs_anterior) * 100

            resultados_por_mes.append({
                "mes": mes.strftime("%Y-%m"),
                "valor": total,
                "ah": ah
            })

        return resultados_por_mes


#relatorio 6

    def calcular_indicadores_dre(self, mes: date) -> List[Dict[str, Any]]:
            """Calcula os indicadores financeiros do DRE para um mês específico.

            Args:
                mes: Data do mês a ser calculado.

            Returns:
                Lista de dicionários com os indicadores, valores e análise vertical (av_dre).
            """
            
            # Query para obter os dados do DRE
            query = text("""
              SELECT categoria, sum(valor) AS valor
              FROM dre
              WHERE id_cliente = ANY (:id_cliente)
                AND visao = 'Competência'
                AND EXTRACT(YEAR FROM data) = :year
                AND EXTRACT(MONTH FROM data) = :month
              group by categoria;
            """)
            params = {
                "id_cliente": self.id_cliente,
                "year": mes.year,
                "month": mes.month
            }
            try:
                result = self.db.execute_query(query, params)
                dados_dre = {row["categoria"]: row["valor"] for _, row in result.iterrows() if row["valor"] is not None}
            except Exception as e:
                raise RuntimeError(f"Erro ao consultar DRE: {str(e)}")

            # Inicializar valores com 0 para categorias que podem não existir
            valores = {
                "Receita de Vendas de Produtos":dados_dre.get("Receita de Vendas de Produtos",0.0),
                "Receita de Prestação de Serviços": dados_dre.get("Receita de Prestação de Serviços", 0.0),
                "Descontos Incondicionais": dados_dre.get("Descontos Incondicionais", 0.0),
                "ICMS": dados_dre.get("ICMS", 0.0),
                "PIS": dados_dre.get("PIS", 0.0),
                "COFINS": dados_dre.get("COFINS", 0.0),
                "ISS": dados_dre.get("ISS", 0.0),
                "Simples Nacional": dados_dre.get("Simples Nacional", 0.0),
                "Outros Tributos de Deduções de Vendas": dados_dre.get("Outros Tributos de Deduções de Vendas", 0.0),
                "Devoluções de Vendas": dados_dre.get("Devoluções de Vendas", 0.0),
                "Custos com Produtos e Serviços": dados_dre.get("Custos com Produtos e Serviços", 0.0),
                "Custos Comerciais": dados_dre.get("Custos Comerciais", 0.0),
                "Despesas Administrativas": dados_dre.get("Despesas Administrativas", 0.0),
                "Despesas com Pessoal": dados_dre.get("Despesas com Pessoal", 0.0),
                "Despesas com Serviços de Terceiros": dados_dre.get("Despesas com Serviços de Terceiros", 0.0),
                "Despesas com Materiais e Equipamentos": dados_dre.get("Despesas com Materiais e Equipamentos", 0.0),
                "Despesas de Marketing": dados_dre.get("Despesas de Marketing", 0.0),
                "Despesas com Desenvolvimento Empresarial": dados_dre.get("Despesas com Desenvolvimento Empresarial", 0.0),
                "Receitas Financeiras": dados_dre.get("Receitas Financeiras", 0.0),
                "Rendimentos de Aplicações": dados_dre.get("Rendimentos de Aplicações", 0.0),
                "Despesas Financeiras": dados_dre.get("Despesas Financeiras", 0.0),
                "Juros Bancários": dados_dre.get("Juros Bancários", 0.0),
                "IRPJ": dados_dre.get("IRPJ", 0.0),
                "CSLL": dados_dre.get("CSLL", 0.0),
                "Investimento de Intangíveis": dados_dre.get("Investimento de Intangíveis", 0.0),
                "Investimento em Imobilizado": dados_dre.get("Investimento em Imobilizado", 0.0),
                "Investimentos em Bens Materiais": dados_dre.get("Investimentos em Bens Materiais", 0.0),
                "Outras saídas não operacionais": dados_dre.get("Outras saídas não operacionais", 0.0),
                "Empréstimos bancários": dados_dre.get("Empréstimos bancários", 0.0),
                "Venda de Imobilizados": dados_dre.get("Venda de Imobilizados", 0.0),
                "Devolução de Pagamentos": dados_dre.get("Devolução de Pagamentos", 0.0),
                "Outras entradas não operacionais": dados_dre.get("Outras entradas não operacionais", 0.0),
                "Perdas Jurídicas": dados_dre.get("Perdas Jurídicas", 0.0),
                "Aplicações Financeiras": dados_dre.get("Aplicações Financeiras", 0.0),
                "Pagamento de Empréstimos": dados_dre.get("Pagamento de Empréstimos", 0.0),
                "Dívidas Passadas": dados_dre.get("Dívidas Passadas", 0.0),
                "Outras saídas não operacionais": dados_dre.get("Outras saídas não operacionais", 0.0),
                "Aporte": dados_dre.get("Capitalização dos sócios", 0.0),
                "Distribuição de Lucros": dados_dre.get("Distribuição de Lucros", 0.0)
                
            }

            # Cálculos dos indicadores
            faturamento = (valores["Receita de Vendas de Produtos"] + valores["Receita de Prestação de Serviços"])
            deducoes_receita_bruta = (valores["Descontos Incondicionais"] + valores["ICMS"] + valores["PIS"] +
                                    valores["COFINS"] + valores["ISS"] +
                                    valores["Outros Tributos de Deduções de Vendas"] + valores["Devoluções de Vendas"])
            custos_variaveis = (valores["Custos com Produtos e Serviços"] + valores["Custos Comerciais"])
            despesas_fixas = (valores["Despesas Administrativas"] + valores["Despesas com Pessoal"] +
                            valores["Despesas com Serviços de Terceiros"] + valores["Despesas com Materiais e Equipamentos"] +
                            valores["Despesas de Marketing"] + valores["Despesas com Desenvolvimento Empresarial"])
            custos_variaveis_deducoes = custos_variaveis + deducoes_receita_bruta
            receitas_financeiras = valores["Receitas Financeiras"] + valores["Rendimentos de Aplicações"]
            despesas_financeiras = valores["Despesas Financeiras"] + valores["Juros Bancários"]
            impostos = (valores["IRPJ"] + valores["CSLL"] + valores["Simples Nacional"])
            lucro_operacional = (faturamento + deducoes_receita_bruta + custos_variaveis + despesas_fixas +
                                receitas_financeiras + despesas_financeiras + impostos)
            investimentos = valores["Investimentos em Bens Materiais"] + valores["Investimento em Imobilizado"] + valores["Investimento de Intangíveis"]
            entradas_nao_operacionais = valores["Empréstimos bancários"] + valores["Venda de Imobilizados"] + valores["Devolução de Pagamentos"] + valores["Outras entradas não operacionais"]
            saidas_nao_operacionais = valores["Perdas Jurídicas"] + valores["Aplicações Financeiras"] + valores["Pagamento de Empréstimos"] + valores["Dívidas Passadas"] + valores["Outras saídas não operacionais"]
            aporte = valores["Aporte"]
            distribuicao_de_lucros = valores["Distribuição de Lucros"]
            lucro_liquido = (faturamento + deducoes_receita_bruta + custos_variaveis + despesas_fixas + receitas_financeiras + despesas_financeiras 
                             + impostos + investimentos +entradas_nao_operacionais + saidas_nao_operacionais + aporte + distribuicao_de_lucros)
            ebitda = (faturamento + deducoes_receita_bruta + custos_variaveis + despesas_fixas)
            #ebitda = (receitas_financeiras + despesas_financeiras + impostos)
            # Lista única de indicadores com análise vertical (av_dre)
            indicadores = [
                {"indicador": "Faturamento", "valor": round(faturamento, 2)},
                {"indicador": "Deduções da Receita Bruta", "valor": round(deducoes_receita_bruta, 2)},
                {"indicador": "Custos Variáveis", "valor": round(custos_variaveis, 2)},
                {"indicador": "Despesas Fixas", "valor": round(despesas_fixas, 2)},
                {"indicador": "EBITDA", "valor": round(ebitda, 2)},
                {"indicador": "Custos Variáveis + Deduções da Receita", "valor": round(custos_variaveis_deducoes, 2)},
                {"indicador": "Custos com Produtos e Serviços", "valor": round(valores["Custos com Produtos e Serviços"], 2)},
                {"indicador": "Lucro Operacional", "valor": round(lucro_operacional, 2)},
                {"indicador": "Lucro Líquido", "valor": round(lucro_liquido, 2)}
            ]

            # Calcular análise vertical (av_dre) para cada indicador
            for indicador in indicadores:
                if faturamento != 0:
                    av_dre = (indicador["valor"] / faturamento) * 100
                else:
                    av_dre = 0.0
                indicador["av_dre"] = round(av_dre, 1)  # Arredondar para 1 casa decimal, conforme o Figma

            return indicadores

  #indicadores do b.i:
    def calcular_indicadores_operacionais(self, mes: date) -> List[Dict[str, Any]]:
        """Calcula os indicadores operacionais e seus valores para um cliente e mês específico, somando valores de indicadores com o mesmo nome.

        Args:
            mes: Data do mês a ser calculado (o dia é ignorado, apenas ano e mês são usados).

        Returns:
            Lista de dicionários com 'indicador', 'total_valor', 'bom', 'ruim', 'sentido' e 'unidade'.
        """
        query = text("""
            SELECT
                indicador,
                bom,
                ruim,
                sentido,
                unidade,
                COALESCE(SUM(valor), 0) AS total_valor
            FROM indicador
            WHERE id_cliente = ANY (:id_cliente)
              AND EXTRACT(YEAR FROM data) = :year
              AND EXTRACT(MONTH FROM data) = :month
              AND bom IS NOT NULL
              AND ruim IS NOT NULL
            GROUP BY indicador, bom, ruim, sentido, unidade
            ORDER BY indicador;
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
                    "indicador": row["indicador"],
                    "total_valor": float(row["total_valor"]) if row["total_valor"] is not None else 0.0,
                    "bom": float(row["bom"]),
                    "ruim":float(row["ruim"]),
                    "sentido": row["sentido"],
                    "unidade": row["unidade"]
                }
                for _, row in result.iterrows()
            ] if not result.empty else []
        except Exception as e:
            raise RuntimeError(f"Erro ao calcular indicadores operacionais: {str(e)}")
