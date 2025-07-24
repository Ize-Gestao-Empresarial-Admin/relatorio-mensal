# src/core/relatorios/relatorio_7.py
from datetime import date
from typing import Optional, List, Dict, Any, Tuple
from src.core.utils import safe_float 
from src.core.indicadores import Indicadores

class Relatorio7:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Gera o relatório financeiro 7 com indicadores operacionais e seus valores.

        Args:
            mes_atual: Data do mês a ser calculado.
            mes_anterior: Data do mês anterior (não usado, incluído para consistência).

        Returns:
            Tupla contendo:
            - Lista de dicionários, cada um com 'categoria' (nome do indicador), 'valor', 'cenario_bom', 
              'cenario_ruim' e 'unidade' (valores possíveis: '%', 'R$' ou 'SU').
            - Dicionário com 'notas' contendo observações automatizadas.
        """
        # Buscar indicadores
        indicadores_resultado = self.indicadores.calcular_indicadores_operacionais(mes_atual)
        
        # Verificar se há indicadores disponíveis
        if not indicadores_resultado:
            # Retornar lista vazia e nota explicativa
            notas_sem_indicadores = (
                "Não há indicadores configurados para este cliente no período selecionado. "
                "Entre em contato com a equipe de desenvolvimento."
            )
            
            return [], {
                "notas": notas_sem_indicadores,
                "sem_indicadores": True
            }
        
        # Notas automatizadas para quando há indicadores
        notas_automatizadas = (
            "O cenário bom/ruim representa x" 
            #bom/ruim devem ser dinâmicos, na tabela puxar "ruim" e "bom" do banco equivalente a "ruim" e "bom" do banco equivalente a categoria
        )
        
        # Lista de valores válidos para unidade
        UNIDADES_VALIDAS = {"%", "R$", "SU"}

        # Construir lista de categorias (cada indicador é uma categoria)
        indicadores_formatados = []
        for i in indicadores_resultado:
            # Verificar se a unidade está nos valores válidos
            unidade = i.get("unidade", "SU")
            if unidade not in UNIDADES_VALIDAS:
                unidade = "SU"  # Usar padrão se inválido
            
            indicador_formatado = {
                "categoria": i["indicador"],
                "valor": safe_float(i["total_valor"]),
                "cenario_bom": safe_float(i["bom"]),
                "cenario_ruim": safe_float(i["ruim"]),
                "unidade": unidade
            }
            indicadores_formatados.append(indicador_formatado)
        
        return indicadores_formatados, {
            "notas": notas_automatizadas,
            "sem_indicadores": False
        }