from datetime import date
from typing import List, Dict, Any
import logging
from src.core.indicadores import Indicadores

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
            for indicador in indicadores_esperados:
                if indicador not in indicadores_dict:
                    logger.error(f"Indicador '{indicador}' não encontrado nos resultados")
                    raise RuntimeError(f"Indicador '{indicador}' não encontrado nos resultados")

            # Extrair valores para as notas
            faturamento = indicadores_dict["Faturamento"]["valor"]
            deducoes = indicadores_dict["Deduções da Receita Bruta"]["valor"]
            custos_variaveis = indicadores_dict["Custos Variáveis"]["valor"]
            despesas_fixas = indicadores_dict["Despesas Fixas"]["valor"]
            ebitda_percentual = indicadores_dict["EBITDA"]["av_dre"]

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