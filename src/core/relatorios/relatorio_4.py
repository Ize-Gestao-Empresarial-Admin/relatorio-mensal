# src/core/relatorios/relatorio_4.py
from datetime import date
from typing import Optional, List, Dict, Any
from src.core.indicadores import Indicadores

class Relatorio4:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> List[Dict[str, Any]]:
        # Calcular mes_anterior se não fornecido
        if mes_anterior is None:
            mes_anterior = date(mes_atual.year if mes_atual.month > 1 else mes_atual.year - 1,
                                mes_atual.month - 1 if mes_atual.month > 1 else 12, 1)

        # Chamar funções de indicadores
        lucro_liquido_resultado = self.indicadores.calcular_lucro_liquido_fc(mes_atual)
        entradas_nao_operacionais_resultado = self.indicadores.calcular_entradas_nao_operacionais_fc(mes_atual)

        # Extrair valores do Lucro Líquido
        receita_atual = next((r['valor'] for r in lucro_liquido_resultado if r['categoria'] == 'Receita'), 0)
        custos_variaveis_atual = next((r['valor'] for r in lucro_liquido_resultado if r['categoria'] == 'Custos Variáveis'), 0)
        despesas_fixas_atual = next((r['valor'] for r in lucro_liquido_resultado if r['categoria'] == 'Despesas Fixas'), 0)
        investimentos_atual = next((r['valor'] for r in lucro_liquido_resultado if r['categoria'] == 'Investimentos'), 0)
        lucro_liquido_atual = receita_atual - custos_variaveis_atual - despesas_fixas_atual - investimentos_atual

        # Análise Vertical (AV) do Lucro Líquido
        av_lucro_liquido = round((lucro_liquido_atual / receita_atual) * 100, 2) if receita_atual else 0

        # Construir subcategorias para Lucro Líquido
        lucro_liquido_categorias = [
            {
                "subcategoria": r["categoria"],
                "valor": r["valor"],
                "av": round(r["av"], 2) if r["av"] is not None else 0,
                "ah": round(r["ah"], 2) if r["ah"] is not None else 0
            } for r in lucro_liquido_resultado
        ]

        # Construir subcategorias para Entradas Não Operacionais (todas disponíveis)
        entradas_nao_operacionais_categorias = [
            {
                "subcategoria": e["categoria_nivel_3"],
                "valor": e["total_valor"],
                "av": round(e["av"], 2) if e["av"] is not None else 0,
                "ah": round(e["ah"], 2) if e["ah"] is not None else 0
            } for e in entradas_nao_operacionais_resultado
        ]

        # Notas automatizadas
        destaques = [
            f"Lucro Líquido: AV={round(av_lucro_liquido, 2)}%"
        ]
        destaques += [f"{r['categoria']}: AV={round(r['av'], 2)}%" for r in lucro_liquido_resultado if r['av'] is not None]
        destaques += [f"{e['categoria_nivel_3']}: AV={round(e['av'], 2)}%" for e in entradas_nao_operacionais_resultado if e['av'] is not None]
        notas_automatizadas = (
            "O Lucro Líquido é calculado subtraindo Custos Variáveis, Despesas Fixas e Investimentos da Receita, representando o resultado financeiro final. "
            "As Entradas Não Operacionais incluem rendimentos e outras receitas não ligadas à operação principal. "
            f"Destaques: {', '.join(destaques)}."
        )

        # Mensagem padrão
        if (receita_atual == 0 and custos_variaveis_atual == 0 and 
            despesas_fixas_atual == 0 and investimentos_atual == 0 and 
            not entradas_nao_operacionais_resultado):
            notas_automatizadas = "Não há dados disponíveis para o período selecionado."

        return [
            {
            "categoria": "Lucro Líquido",
            "valor": lucro_liquido_atual,
            "subcategorias": lucro_liquido_categorias,
            },
            {
            "categoria": "Entradas Não Operacionais",
            "valor": sum(e["total_valor"] for e in entradas_nao_operacionais_resultado),
            "subcategorias": entradas_nao_operacionais_categorias,
            }
        ], {
            "notas": notas_automatizadas
        }