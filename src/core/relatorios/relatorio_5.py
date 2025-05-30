# src/core/relatorios/relatorio_5.py
from datetime import date
from typing import Optional, List, Dict, Any
from src.core.indicadores import Indicadores
from dateutil.relativedelta import relativedelta

class Relatorio5:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> List[Dict[str, Any]]:
        """Gera o relatório financeiro 5 - Fechamento de Fluxo de Caixa.

        Args:
            mes_atual: Data do mês a ser calculado.
            mes_anterior: Data do mês anterior (não usado diretamente, incluído para consistência).

        Returns:
            Lista de dicionários com categorias, valores, subcategorias e análise temporal.
        """
         # Calcula mês anterior automaticamente se não for passado
        if mes_anterior is None:
            mes_anterior = mes_atual - relativedelta(months=1)

        # Parte 1: Cálculo das categorias principais (Saídas Não Operacionais e Geração de Caixa)
        saidas_nao_operacionais_resultado = self.indicadores.calcular_saidas_nao_operacionais_fc(mes_atual)
        geracao_de_caixa_resultado = self.indicadores.calcular_geracao_de_caixa_fc(mes_atual)

        # Construir subcategorias para Geração de Caixa
        geracao_de_caixa_categorias = [
            {
                "subcategoria": r["categoria"],
                "valor": r["valor"],
                "av": round(r["av"], 2) if r["av"] is not None else 0,
                "ah": round(r["ah"], 2) if r["ah"] is not None else 0
            } for r in geracao_de_caixa_resultado
        ]

        # Calcular o valor total da Geração de Caixa corretamente
        lucro_liquido_valor = next((r["valor"] for r in geracao_de_caixa_resultado if r["categoria"] == "Lucro Líquido"), 0)
        entradas_nao_operacionais_valor = next((r["valor"] for r in geracao_de_caixa_resultado if r["categoria"] == "Entradas Não Operacionais"), 0)
        saidas_nao_operacionais_valor = next((r["valor"] for r in geracao_de_caixa_resultado if r["categoria"] == "Saídas Não Operacionais"), 0)
        total_geracao_de_caixa = lucro_liquido_valor + entradas_nao_operacionais_valor - saidas_nao_operacionais_valor

        # Parte 2: Análise Temporal da Geração de Caixa (3 meses)
        analise_temporal_resultado = self.indicadores.calcular_geracao_de_caixa_temporal_fc(mes_atual)

        # Calcular a média da Geração de Caixa dos 3 meses
        if analise_temporal_resultado:
            media_geracao_de_caixa = sum(r["valor"] for r in analise_temporal_resultado) / len(analise_temporal_resultado)
        else:
            media_geracao_de_caixa = 0.0

        # Notas automatizadas para a Parte 1
        destaques = [f"{r['categoria']}: AV={round(r['av'], 2)}%" for r in geracao_de_caixa_resultado if r['av'] is not None]
        notas_automatizadas = (
            "A Geração de Caixa é calculada como  "
            f"Destaques: {', '.join(destaques)}. "
            f"Média da Geração de Caixa (últimos 3 meses): {round(media_geracao_de_caixa, 2)}."
        )

        # Mensagem padrão se não houver dados
        if not geracao_de_caixa_resultado and not saidas_nao_operacionais_resultado:
            notas_automatizadas = "Não há dados disponíveis para o período selecionado."

        return [
            {
                "categoria": "Saídas Não Operacionais",
                "valor": saidas_nao_operacionais_resultado[0]["valor"]
            },
            {
                "categoria": "Geração de Caixa",
                "valor": total_geracao_de_caixa,
                "subcategorias": geracao_de_caixa_categorias,
                "analise_temporal": {
                    "meses": [
                        {
                            "mes": r["mes"],
                            "valor": round(r["valor"], 2),  # Arredondar valores para exibição
                            "ah": round(r["ah"], 2)  # Arredondar ah para exibição
                        } for r in analise_temporal_resultado
                    ],
                    "media": round(media_geracao_de_caixa, 2)
                }
            }
        ], {
            "notas": notas_automatizadas
        }
        
        
#FICOU FALTANDO O CAIXA ACUMULADO, NAO CONSEGUI DESCOBRIR COMO CALCULAR