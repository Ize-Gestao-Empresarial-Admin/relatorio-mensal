# debug_indicadores.py - Arquivo temporário para debug
from datetime import date
from typing import Union, List, Dict, Any, Optional
from sqlalchemy import text
from src.database.db_utils import DatabaseConnection

class IndicadoresDebug:
    def __init__(self, id_cliente: Union[int, List[int]], db_connection: DatabaseConnection):
        self.id_cliente = id_cliente
        self.db = db_connection

    def calcular_geracao_de_caixa_fc(self, mes: date) -> List[Dict[str, Any]]:
        """Versão de debug da função calcular_geracao_de_caixa_fc."""
        print(f"\n=== DEBUG calcular_geracao_de_caixa_fc ===")
        print(f"Cliente ID: {self.id_cliente}")
        print(f"Mês: {mes}")
        
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
                      ((l.valor - lp.prev_valor) / ABS(lp.prev_valor)) * 100
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
        
        print(f"Parâmetros da query: {params}")
        
        try:
            result = self.db.execute_query(query, params)
            print(f"Resultado da query (DataFrame): {result}")
            
            if result.empty:
                print("ATENÇÃO: Query retornou resultado vazio!")
                return []
            
            # Processar resultado
            resultado_processado = []
            for _, row in result.iterrows():
                item = {
                    "categoria": row["categoria"],
                    "valor": float(row["valor"]) if row["valor"] is not None else 0,
                    "av": float(row["av"]) if row["av"] is not None else 0,
                    "ah": float(row["ah"]) if row["ah"] is not None else 0
                }
                resultado_processado.append(item)
                print(f"Item processado: {item}")
            
            print(f"Resultado final: {resultado_processado}")
            return resultado_processado
            
        except Exception as e:
            print(f"ERRO na query: {str(e)}")
            raise RuntimeError(f"Erro ao calcular geração de caixa: {str(e)}")

    def calcular_geracao_de_caixa_temporal_fc(self, mes_atual: date) -> List[Dict[str, Any]]:
        """Versão de debug da função temporal."""
        print(f"\n=== DEBUG calcular_geracao_de_caixa_temporal_fc ===")
        print(f"Mês atual: {mes_atual}")
        
        # Definir os 3 meses a serem calculados
        meses = []
        for i in range(3):
            ano = mes_atual.year if mes_atual.month > i else mes_atual.year - 1
            mes = mes_atual.month - i if mes_atual.month > i else 12 - (i - mes_atual.month)
            meses.append(date(ano, mes, 1))

        print(f"Meses a serem calculados: {[m.strftime('%Y-%m') for m in meses]}")

        # Calcular a Geração de Caixa para cada mês
        resultados_por_mes = []
        for i, mes in enumerate(meses):
            print(f"\n--- Processando mês {mes.strftime('%Y-%m')} ---")
            
            # Calcular a Geração de Caixa do mês atual
            geracao_de_caixa = self.calcular_geracao_de_caixa_fc(mes)
            print(f"Geração de caixa retornada: {geracao_de_caixa}")
            
            # Simplesmente somar todos os valores
            total = sum(r["valor"] for r in geracao_de_caixa)
            print(f"Total calculado: {total}")

            # Calcular o valor do mês anterior para o ah
            mes_anterior = date(mes.year if mes.month > 1 else mes.year - 1,
                              mes.month - 1 if mes.month > 1 else 12, 1)
            print(f"Mês anterior para AH: {mes_anterior.strftime('%Y-%m')}")
            
            geracao_de_caixa_anterior = self.calcular_geracao_de_caixa_fc(mes_anterior)
            total_anterior = sum(r["valor"] for r in geracao_de_caixa_anterior)
            print(f"Total anterior: {total_anterior}")

            # Calcular o ah
            if total_anterior == 0:
                ah = 0
            else:
                valor_abs_atual = abs(total)
                valor_abs_anterior = abs(total_anterior)
                ah = ((valor_abs_atual - valor_abs_anterior) / valor_abs_anterior) * 100

            print(f"AH calculado: {ah}")

            resultado_mes = {
                "mes": mes.strftime("%Y-%m"),
                "valor": total,
                "ah": ah
            }
            resultados_por_mes.append(resultado_mes)
            print(f"Resultado do mês: {resultado_mes}")

        print(f"\nResultado final temporal: {resultados_por_mes}")
        return resultados_por_mes