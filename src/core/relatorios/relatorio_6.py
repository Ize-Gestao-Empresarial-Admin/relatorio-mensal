from datetime import date
from typing import List, Dict, Any
import logging
import math
import numpy as np
from src.core.indicadores import Indicadores
from src.core.utils import safe_float

# Configurar logging para depuração
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Relatorio6:
    def __init__(self, indicadores: Indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente

    def gerar_relatorio(self, mes: date) -> tuple[List[Dict[str, Any]], Dict[str, str]]:
        """Gera o relatório financeiro 6 - Indicadores DRE.

        Args:
            mes: Data do mês a ser calculado.

        Returns:
            Tupla contendo a lista de dicionários com indicadores e um dicionário com notas automatizadas.

        Raises:
            RuntimeError: Se houver erro ao calcular os indicadores ou formatar as notas.
        """
        try:
            # Obter os indicadores calculados
            indicadores_resultado = self.indicadores.calcular_indicadores_dre(mes)

            # Mapear indicadores esperados para as notas
            indicadores_esperados = [
                "Faturamento",
                "Deduções da Receita Bruta",
                "Custos Variáveis",
                "Despesas Fixas",
                "EBITDA"
            ]
            
            # Criar dicionário para facilitar acesso aos valores dos indicadores
            indicadores_dict = {item["indicador"]: item for item in indicadores_resultado}
            
            # Verificar se todos os indicadores necessários estão presentes
            indicadores_presentes = all(indicador in indicadores_dict for indicador in indicadores_esperados)
            
            # Verificar se há dados válidos - similar à lógica do relatório 4
            dados_validos = False
            if indicadores_presentes:
                # Verifica se pelo menos um dos valores principais não é nulo, zero ou NaN
                for indicador in indicadores_esperados:
                    valor = indicadores_dict[indicador]["valor"]
                    if valor is not None and valor != 0 and not (isinstance(valor, float) and (math.isnan(valor) or np.isnan(valor))):
                        dados_validos = True
                        break
            
            # Gerar notas automatizadas baseadas na disponibilidade de dados
            if not indicadores_presentes or not dados_validos:
                notas_automatizadas = "Não há dados disponíveis para o período selecionado."
            else:
                # Extrair valores para as notas, usando safe_float para garantir que valores None ou NaN sejam tratados
                faturamento = safe_float(indicadores_dict["Faturamento"]["valor"], 0.0)
                deducoes = safe_float(indicadores_dict["Deduções da Receita Bruta"]["valor"], 0.0)
                custos_variaveis = safe_float(indicadores_dict["Custos Variáveis"]["valor"], 0.0)
                despesas_fixas = safe_float(indicadores_dict["Despesas Fixas"]["valor"], 0.0)
                ebitda_percentual = safe_float(indicadores_dict["EBITDA"]["av_dre"], 0.0)

                # Gerar notas automatizadas com valores formatados
                notas_automatizadas = (
                    f"No mês, tivemos um total de vendas no montante de R$ {faturamento:,.2f}, "
                    f"seguido das deduções da receita bruta de R$ {deducoes:,.2f}, "
                    f"Custos Variáveis em R$ {custos_variaveis:,.2f}, "
                    f"Despesas Fixas de R$ {despesas_fixas:,.2f}, "
                    f"fechando o mês com um EBITDA de {ebitda_percentual:.1f}% em relação ao faturamento!"
                )

            return indicadores_resultado, {"notas": notas_automatizadas}

        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {str(e)}")
            raise RuntimeError(f"Erro ao gerar relatório: {str(e)}")