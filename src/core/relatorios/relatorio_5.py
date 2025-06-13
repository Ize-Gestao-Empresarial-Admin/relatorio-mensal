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
        try:
            saidas_nao_operacionais_resultado = self.indicadores.calcular_saidas_nao_operacionais_fc(mes_atual)
        except Exception:
            saidas_nao_operacionais_resultado = []
            
        try:
            geracao_de_caixa_resultado = self.indicadores.calcular_geracao_de_caixa_fc(mes_atual)
        except Exception:
            geracao_de_caixa_resultado = []
        
        # Dados do mês anterior para comparação
        try:
            saidas_nao_operacionais_anterior = self.indicadores.calcular_saidas_nao_operacionais_fc(mes_anterior)
        except Exception:
            saidas_nao_operacionais_anterior = []
            
        try:
            geracao_de_caixa_anterior = self.indicadores.calcular_geracao_de_caixa_fc(mes_anterior)
        except Exception:
            geracao_de_caixa_anterior = []

        # Calcular o valor total da Geração de Caixa do mês atual - MELHORADO: usar safe_float
        lucro_liquido_valor = 0
        entradas_nao_operacionais_valor = 0
        saidas_nao_operacionais_valor = 0
        
        for r in geracao_de_caixa_resultado:
            if r.get("categoria") == "Lucro Líquido":
                lucro_liquido_valor = safe_float(r.get("valor", 0))
            elif r.get("categoria") == "Entradas Não Operacionais":
                entradas_nao_operacionais_valor = safe_float(r.get("valor", 0))
            elif r.get("categoria") == "Saídas Não Operacionais":
                saidas_nao_operacionais_valor = safe_float(r.get("valor", 0))
        
        total_geracao_de_caixa = lucro_liquido_valor + entradas_nao_operacionais_valor - saidas_nao_operacionais_valor

        # Calcular o valor total da Geração de Caixa do mês anterior - MELHORADO: usar safe_float
        lucro_liquido_anterior = 0
        entradas_nao_operacionais_anterior = 0
        saidas_nao_operacionais_anterior_val = 0
        
        for r in geracao_de_caixa_anterior:
            if r.get("categoria") == "Lucro Líquido":
                lucro_liquido_anterior = safe_float(r.get("valor", 0))
            elif r.get("categoria") == "Entradas Não Operacionais":
                entradas_nao_operacionais_anterior = safe_float(r.get("valor", 0))
            elif r.get("categoria") == "Saídas Não Operacionais":
                saidas_nao_operacionais_anterior_val = safe_float(r.get("valor", 0))
        
        total_geracao_de_caixa_anterior = lucro_liquido_anterior + entradas_nao_operacionais_anterior - saidas_nao_operacionais_anterior_val

        # CORRIGIDO: Buscar receita total corretamente - MELHORADO: usar safe_float
        receita_total = 0
        try:
            # Primeiro tentar buscar diretamente da função de receitas
            receitas_fc = self.indicadores.calcular_receitas_fc(mes_atual, "3.%")
            receita_total = sum(safe_float(r.get("total_categoria", 0)) for r in receitas_fc)
        except:
            # Se falhar, tentar buscar do lucro líquido
            try:
                lucro_liquido_resultado = self.indicadores.calcular_lucro_liquido_fc(mes_atual)
                for r in lucro_liquido_resultado:
                    if r.get("categoria") == "Receita":
                        receita_total = safe_float(r.get("valor", 0))
                        break
            except:
                receita_total = 0

        # CORRIGIDO: Construir subcategorias para Geração de Caixa seguindo o padrão dos outros relatórios
        geracao_de_caixa_categorias = []
        for r in geracao_de_caixa_resultado:
            valor = safe_float(r.get("valor", 0))
            av = safe_float(r.get("av", 0))
            ah = safe_float(r.get("ah", 0))
            
            # CORRIGIDO: Usar AV (Análise Vertical) já calculado pelo indicador
            # que representa o percentual em relação à receita total
            representatividade_av = abs(av)  # Usar o AV que vem do indicador
            
            # CORRIGIDO: Para barra_rep, usar a mesma lógica dos outros relatórios
            # Calcular proporção do valor absoluto em relação ao total de valores absolutos
            total_valores_absolutos = sum(abs(safe_float(item.get("valor", 0))) for item in geracao_de_caixa_resultado)
            barra_rep = 0
            if total_valores_absolutos > 0:
                barra_rep = round((abs(valor) / total_valores_absolutos) * 100, 2)
                
            geracao_de_caixa_categorias.append({
                "subcategoria": r.get("categoria", "N/A"),
                "valor": valor,
                "av": round(av, 2),
                "ah": round(ah, 2),
                "representatividade": representatividade_av,  # CORRIGIDO: usar AV do indicador
                "barra_rep": barra_rep  # NOVO: adicionar barra_rep seguindo padrão dos outros relatórios
            })

        # Parte 2: Análise Temporal da Geração de Caixa (3 meses) - MELHORADO: usar safe_float
        try:
            analise_temporal_resultado = self.indicadores.calcular_geracao_de_caixa_temporal_fc(mes_atual)
        except Exception:
            analise_temporal_resultado = []

        # Calcular a média da Geração de Caixa dos 3 meses - MELHORADO: usar safe_float
        media_geracao_de_caixa = 0.0
        if analise_temporal_resultado:
            valores_validos = []
            for r in analise_temporal_resultado:
                valor = safe_float(r.get("valor", 0))
                valores_validos.append(valor)
            
            if valores_validos:
                media_geracao_de_caixa = sum(valores_validos) / len(valores_validos)

        # Calcula variações (AH) - MELHORADO: usar safe_float para tratar valores inválidos
        geracao_caixa_ah = 0
        if total_geracao_de_caixa_anterior != 0:
            try:
                ah_calculado = ((total_geracao_de_caixa / total_geracao_de_caixa_anterior - 1) * 100)
                geracao_caixa_ah = round(safe_float(ah_calculado), 2)
            except (ZeroDivisionError, TypeError, ValueError):
                geracao_caixa_ah = 0

        # NOVO: Calcular caixa acumulado - MELHORADO: usar safe_float
        caixa_acumulado = 0
        if analise_temporal_resultado:
            valores_acumulados = []
            for r in analise_temporal_resultado:
                valor = safe_float(r.get("valor", 0))
                valores_acumulados.append(valor)
            
            caixa_acumulado = sum(valores_acumulados)

        # NOVO: Formatar as notas automáticas seguindo o padrão solicitado - MELHORADO: usar safe_float
        if total_geracao_de_caixa != 0 and receita_total != 0:
            try:
                # Determinar se é composição ou decomposição
                tipo_movimento = "composição" if total_geracao_de_caixa > 0 else "decomposição"
                
                # Calcular percentual em relação à receita
                percentual_receita = (abs(total_geracao_de_caixa) / abs(receita_total)) * 100
                percentual_receita = round(safe_float(percentual_receita), 2)
                
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
            except Exception:
                notas_automatizadas = "Não há dados disponíveis para o período selecionado."
        else:
            notas_automatizadas = "Não há dados disponíveis para o período selecionado."

        # MELHORADO: Garantir que saídas não operacionais seja sempre um valor válido usando safe_float
        saidas_valor = 0
        if saidas_nao_operacionais_resultado:
            saidas_valor = safe_float(saidas_nao_operacionais_resultado[0].get("valor", 0))

        # MELHORADO: Processar análise temporal com safe_float
        meses_processados = []
        for r in analise_temporal_resultado:
            valor = safe_float(r.get("valor", 0))
            ah = safe_float(r.get("ah", 0))
            
            meses_processados.append({
                "mes": r.get("mes", ""),
                "valor": round(valor, 2),
                "ah": round(ah, 2)
            })

        # CORRIGIDO: Calcular AV da categoria principal seguindo padrão dos outros relatórios
        av_categoria = 0
        if receita_total != 0:
            av_categoria = round(safe_float((total_geracao_de_caixa / receita_total) * 100), 2)

        return [
            {
                "categoria": "Saídas Não Operacionais",
                "valor": saidas_valor
            },
            {
                "categoria": "Geração de Caixa",
                "valor": total_geracao_de_caixa,
                "av_categoria": av_categoria,  # CORRIGIDO: usar percentual em relação à receita
                "subcategorias": geracao_de_caixa_categorias,
                "analise_temporal": {
                    "meses": meses_processados,
                    "media": round(safe_float(media_geracao_de_caixa), 2)
                }
            }
        ], {
            "notas": notas_automatizadas
        }