#src/core/indicadores.py
from datetime import date
from typing import List, Optional
from src.database.db_utils import DatabaseConnection
import pandas as pd
from sqlalchemy import text

class Indicadores:
    def __init__(self, id_cliente: int, db_connection: DatabaseConnection):
        self.id_cliente = id_cliente
        self.db = db_connection

    def calcular_nivel_1(self, mes: date, categorias: List[str]) -> float:
        """Calcula o total para categorias específicas em um mês.

        Args:
            mes: Data do mês a ser calculado.
            categorias: Lista de categorias (nivel_1) a serem somadas.

        Returns:
            Total calculado ou 0 se não houver dados.
        """
        categorias_str = ", ".join(f"'{cat}'" for cat in categorias)
        query = f"""
            SELECT SUM(f.valor) as total
            FROM fc f
            WHERE f.nivel_1 IN ({categorias_str})
            AND f.visao = 'Realizado'
            AND f.id_cliente = {self.id_cliente}
            AND EXTRACT(YEAR FROM f.data) = {mes.year}
            AND EXTRACT(MONTH FROM f.data) = {mes.month};
        """
        resultado = self.db.execute_query(query)
        total = resultado.iloc[0]['total']
        return total if total is not None else 0


    def calcular_categoria_dre(self, mes: date, categorias: List[str]) -> float:
            """Calcula o total para categorias específicas em um mês (DRE).

            Args:
                mes: Data do mês a ser calculado.
                categorias: Lista de categorias a serem somadas.

            Returns:
                Total calculado ou 0 se não houver dados.
            """
            categorias_str = ", ".join(f"'{cat}'" for cat in categorias)
            query = f"""
                SELECT SUM(d.valor) as total
                FROM dre d
                WHERE d.categoria IN ({categorias_str})
                AND d.visao = 'Competência'
                AND d.id_cliente = {self.id_cliente}
                AND EXTRACT(YEAR FROM d.data) = {mes.year}
                AND EXTRACT(MONTH FROM d.data) = {mes.month};
            """
            resultado = self.db.execute_query(query)
            total = resultado.iloc[0]['total']
            return total if total is not None else 0
    
    def calcular_nivel_lucros(self, mes: date, categorias: List[str]) -> float:
            """Calcula o total para categorias específicas em um mês (Análise de Lucros)."""
            categorias_str = ", ".join(f"'{cat}'" for cat in categorias)
            query = f"""
                SELECT SUM(f.valor) as total
                FROM fc f
                WHERE f.nivel_1 IN ({categorias_str})
                AND f.visao = 'Realizado'
                AND f.id_cliente = {self.id_cliente}
                AND EXTRACT(YEAR FROM f.data) = {mes.year}
                AND EXTRACT(MONTH FROM f.data) = {mes.month};
            """
            resultado = self.db.execute_query(query)
            total = resultado.iloc[0]['total']
            return total if total is not None else 0
        
    # ### Página 4 - Evolução - Comparativo da Receita e Geração de Caixa - puxar do fluxo de caixa
    def calcular_nivel_evolucao(self, mes: date, categorias: List[str]) -> float:
        """Calcula o total para categorias específicas em um mês (Evolução - Relatório 4)."""
        categorias_str = ", ".join(f"'{cat}'" for cat in categorias)
        query = f"""
            SELECT SUM(f.valor) as total
            FROM fc f
            WHERE f.nivel_1 IN ({categorias_str})
            AND f.visao = 'Realizado'
            AND f.id_cliente = {self.id_cliente}
            AND EXTRACT(YEAR FROM f.data) = {mes.year}
            AND EXTRACT(MONTH FROM f.data) = {mes.month};
        """
        resultado = self.db.execute_query(query)
        total = resultado.iloc[0]['total']
        return total if total is not None else 0
    
    # ### Página 5 - Página 5 - Indicadores - puxar da tabela de indicadores e criar ah e av especifico deles
    def calcular_indicadores(self, mes: date, indicadores: List[str]) -> dict:
        """Consulta indicadores específicos da tabela 'indicador' para um mês."""
        indicadores_str = ", ".join(f"'{ind}'" for ind in indicadores)
        query = f"""
            SELECT i.indicador, i.valor as total
            FROM indicador i
            WHERE i.indicador IN ({indicadores_str})
            AND i.id_cliente = {self.id_cliente}
            AND EXTRACT(YEAR FROM i.data) = {mes.year}
            AND EXTRACT(MONTH FROM i.data) = {mes.month};
        """
        with self.db.engine.connect() as conn:
            result = conn.execute(text(query))
            resultado = pd.DataFrame(result.fetchall(), columns=['indicador', 'total'])

        indicadores_dict = (
            {row['indicador']: row['total'] if pd.notna(row['total']) else 0 for _, row in resultado.iterrows()}
            if not resultado.empty
            else {ind: 0 for ind in indicadores}
        )

        return indicadores_dict

    def buscar_indicadores_disponiveis(self) -> List[str]:
        """Busca todos os indicadores distintos disponíveis para o cliente no banco."""
        query = f"""
            SELECT DISTINCT i.indicador
            FROM indicador i
            WHERE i.id_cliente = {self.id_cliente};
        """
        with self.db.engine.connect() as conn:
            result = conn.execute(text(query))
            indicadores = [row[0] for row in result.fetchall()]
        return indicadores if indicadores else []