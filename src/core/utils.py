# src/core/utils.py
from cmath import nan
from typing import List, Dict, Any
import math

import math
from typing import Any, Union

def safe_float(value: Any, default: float = 0.0) -> Union[float, str]:
    """
    Converte um valor para float de forma segura.
    - Retorna default para None, NaN e conversões inválidas.
    - Retorna "N/A" para valores infinitos.
    """
    try:
        f = float(value)
        if math.isnan(f):
            return default
        if math.isinf(f):
            return 0
        return f
    except (TypeError, ValueError):
        return default


def calcular_outras_categorias(
    items: List[Dict[str, Any]],
    items_anterior: List[Dict[str, Any]],
    total_atual: float,
    total_anterior: float,
    receita_total: float,
    chave_valor: str = "valor",
    chave_nome: str = "categoria",
    top_n: int = 3,
    usar_valor_abs: bool = False
) -> List[Dict[str, Any]]:
    """
    Calcula subcategorias principais e agrupa o restante em 'Outras categorias'.

    Args:
        items: Lista de dicionários com os dados do período atual.
        items_anterior: Lista de dicionários com os dados do período anterior.
        total_atual: Valor total da categoria no período atual.
        total_anterior: Valor total da categoria no período anterior.
        receita_total: Valor total da receita para cálculo de AV.
        chave_valor: Chave do dicionário que contém o valor a ser somado.
        chave_nome: Chave do dicionário que contém o nome da subcategoria.
        top_n: Número de subcategorias principais a serem mantidas.
        usar_valor_abs: Se True, usa valor absoluto para ordenação e cálculos.

    Returns:
        Lista de dicionários com subcategorias, incluindo 'Outras categorias' se aplicável.
    """
    # Ordena itens por valor (absoluto, se especificado)
    ordenados = sorted(
        items,
        key=lambda x: abs(safe_float(x.get(chave_valor, 0))) if usar_valor_abs else safe_float(x.get(chave_valor, 0)),
        reverse=True
    )
    
    # Calcula totais das subcategorias
    total_subcategorias = sum(
        abs(safe_float(item.get(chave_valor, 0))) if usar_valor_abs else safe_float(item.get(chave_valor, 0))
        for item in items
    ) if items else 0

    # Gera lista de subcategorias principais (top N)
    resultado = [
        {
            "subcategoria": item.get(chave_nome, "N/A"),
            "valor": safe_float(item.get(chave_valor, 0)),
            "av": round(safe_float(item.get("av", 0)), 2),
            "ah": round(safe_float(item.get("ah", 0)), 2),
            "representatividade": round(
                (abs(safe_float(item.get(chave_valor, 0))) / total_subcategorias) * 100, 2
            ) if total_subcategorias != 0 else 0
        } for item in ordenados[:top_n]
    ]

    # Calcula valores para "Outras categorias"
    outras_valor = sum(
        abs(safe_float(item.get(chave_valor, 0))) if usar_valor_abs else safe_float(item.get(chave_valor, 0))
        for item in ordenados[top_n:]
    ) if len(ordenados) > top_n else 0

    outras_anterior = sum(
        abs(safe_float(item.get(chave_valor, 0))) if usar_valor_abs else safe_float(item.get(chave_valor, 0))
        for item in sorted(
            items_anterior,
            key=lambda x: abs(safe_float(x.get(chave_valor, 0))) if usar_valor_abs else safe_float(x.get(chave_valor, 0)),
            reverse=True
        )[top_n:]
    ) if len(items_anterior) > top_n else 0

    # Calcula AV (em relação à receita total) e AH para "Outras categorias"
    outras_av = round(
        (outras_valor / receita_total) * 100, 2
    ) if receita_total != 0 else 0
    outras_ah = round(
        ((outras_valor / outras_anterior) - 1) * 100, 2
    ) if outras_anterior != 0 else 0

    # Adiciona "Outras categorias" se houver valores
    if outras_valor != 0:  # Alterado para != 0 para capturar valores negativos
        resultado.append({
            "subcategoria": "Outras categorias",
            "valor": -outras_valor if usar_valor_abs else outras_valor,
            "av": outras_av,
            "ah": outras_ah,
            "representatividade": round(
                (abs(outras_valor) / total_subcategorias) * 100, 2
            ) if total_subcategorias != 0 else 0
        })

    return resultado