# src/core/relatorios/relatorio_5.py
from datetime import date
from typing import Optional, List, Dict, Any
from src.core.indicadores import Indicadores
from dateutil.relativedelta import relativedelta
from src.core.utils import safe_float

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
        
        # Dados do mês anterior para comparação
        saidas_nao_operacionais_anterior = self.indicadores.calcular_saidas_nao_operacionais_fc(mes_anterior)
        geracao_de_caixa_anterior = self.indicadores.calcular_geracao_de_caixa_fc(mes_anterior)

        # Calcular o valor total da Geração de Caixa do mês atual
        lucro_liquido_valor = next((r["valor"] for r in geracao_de_caixa_resultado if r["categoria"] == "Lucro Líquido"), 0)
        entradas_nao_operacionais_valor = next((r["valor"] for r in geracao_de_caixa_resultado if r["categoria"] == "Entradas Não Operacionais"), 0)
        saidas_nao_operacionais_valor = next((r["valor"] for r in geracao_de_caixa_resultado if r["categoria"] == "Saídas Não Operacionais"), 0)
        total_geracao_de_caixa = lucro_liquido_valor + entradas_nao_operacionais_valor - saidas_nao_operacionais_valor

        # Calcular o valor total da Geração de Caixa do mês anterior
        lucro_liquido_anterior = next((r["valor"] for r in geracao_de_caixa_anterior if r["categoria"] == "Lucro Líquido"), 0)
        entradas_nao_operacionais_anterior = next((r["valor"] for r in geracao_de_caixa_anterior if r["categoria"] == "Entradas Não Operacionais"), 0)
        saidas_nao_operacionais_anterior = next((r["valor"] for r in geracao_de_caixa_anterior if r["categoria"] == "Saídas Não Operacionais"), 0)
        total_geracao_de_caixa_anterior = lucro_liquido_anterior + entradas_nao_operacionais_anterior - saidas_nao_operacionais_anterior

        # Calcular a representatividade para o tamanho das barras
        total_positivo = sum(safe_float(abs(r["valor"])) for r in geracao_de_caixa_resultado)
        
        # Construir subcategorias para Geração de Caixa com representatividade
        geracao_de_caixa_categorias = []
        for r in geracao_de_caixa_resultado:
            # Calcular a representatividade para o gráfico de barras
            representatividade = 0
            if total_positivo > 0:
                representatividade = round((abs(r["valor"]) / total_positivo) * 100, 2)
                
            geracao_de_caixa_categorias.append({
                "subcategoria": r["categoria"],
                "valor": r["valor"],
                "av": round(r["av"], 2) if r["av"] is not None else 0,
                "ah": round(r["ah"], 2) if r["ah"] is not None else 0,
                "representatividade": representatividade  # Adiciona representatividade para as barras
            })

        # Parte 2: Análise Temporal da Geração de Caixa (3 meses)
        analise_temporal_resultado = self.indicadores.calcular_geracao_de_caixa_temporal_fc(mes_atual)

        # Calcular a média da Geração de Caixa dos 3 meses
        if analise_temporal_resultado:
            media_geracao_de_caixa = sum(r["valor"] for r in analise_temporal_resultado) / len(analise_temporal_resultado)
        else:
            media_geracao_de_caixa = 0.0

        # Calcula variações (AH)
        geracao_caixa_ah = round(
            ((total_geracao_de_caixa / total_geracao_de_caixa_anterior - 1) * 100)
            if total_geracao_de_caixa_anterior != 0 else 0, 2
        )
        
        # CORRIGIDO: Buscar receita total corretamente
        receita_total = 0
        try:
            # Primeiro tentar buscar diretamente da função de receitas
            receitas_fc = self.indicadores.calcular_receitas_fc(mes_atual, "3.%")
            receita_total = sum(r["total_categoria"] for r in receitas_fc)
        except:
            # Se falhar, tentar buscar do lucro líquido
            lucro_liquido_resultado = self.indicadores.calcular_lucro_liquido_fc(mes_atual)
            receita_total = next((r["valor"] for r in lucro_liquido_resultado if r["categoria"] == "Receita"), 0)

        # NOVO: Calcular caixa acumulado (último valor da análise temporal)
        caixa_acumulado = 0
        if analise_temporal_resultado:
            # Somar todos os valores da análise temporal para obter o acumulado
            caixa_acumulado = sum(r["valor"] for r in analise_temporal_resultado)

        # NOVO: Formatar as notas automáticas seguindo o padrão solicitado
        if total_geracao_de_caixa != 0 and receita_total != 0:
            # Determinar se é composição ou decomposição
            tipo_movimento = "composição" if total_geracao_de_caixa > 0 else "decomposição"
            
            # Calcular percentual em relação à receita
            percentual_receita = round((abs(total_geracao_de_caixa) / abs(receita_total)) * 100, 2)
            
            # Formatar o valor com sinal
            valor_formatado = f"R$ {abs(total_geracao_de_caixa):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            sinal = "+" if total_geracao_de_caixa > 0 else "-"
            
            # Formatar caixa acumulado
            caixa_acumulado_formatado = f"R$ {caixa_acumulado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            notas_automatizadas = (
                f"Por fim, ao confrontar todas as entradas e saídas registradas no mês, "
                f"ficamos com um resultado de ({sinal} {valor_formatado}), que representa uma "
                f"{tipo_movimento} de caixa de {percentual_receita}% em relação à Receita Total. "
                f"Assim, fechamos o mês com um resultado caixa acumulado de {caixa_acumulado_formatado}."
            )
        else:
            notas_automatizadas = "Não há dados disponíveis para o período selecionado."

        return [
            {
                "categoria": "Saídas Não Operacionais",
                "valor": saidas_nao_operacionais_resultado[0]["valor"] if saidas_nao_operacionais_resultado else 0
            },
            {
                "categoria": "Geração de Caixa",
                "valor": total_geracao_de_caixa,
                "av_categoria": round((total_geracao_de_caixa / total_positivo) * 100, 2) if total_positivo > 0 else 0,
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