# src/rendering/renderers/relatorio3_renderer.py
from typing import Dict, Any, List, Tuple, Union
from src.rendering.renderers.base_renderer import BaseRenderer
import os
import base64
import logging
logger = logging.getLogger(__name__)

class Relatorio3Renderer(BaseRenderer):
    """
    Renderizador para o Relatório 3 - Análise de Lucro Operacional e Investimentos.
    Converte os dados do relatório em HTML para posterior geração de PDF.
    """
    
    def __init__(self):
        super().__init__()
        # Carregar o template do relatório 3
        self.template = self.env.get_template("relatorio3/template.html")

    def render(self, data: Union[List[Dict[str, Any]], Tuple[List[Dict[str, Any]], Dict[str, str]]], 
               cliente_nome: str, mes_nome: str, ano: int) -> str:
        """
        Renderiza os dados do Relatório 3 em HTML.
        
        Args:
            data: Dados do relatório ou tupla (dados, notas)
            cliente_nome: Nome do cliente
            mes_nome: Nome do mês
            ano: Ano do relatório
            
        Returns:
            HTML formatado
        """
        # Extrair dados na estrutura correta
        if isinstance(data, tuple) and len(data) == 2:
            relatorio_data = data[0]
            notas = data[1].get("notas", "")
        else:
            relatorio_data = data
            notas = ""
        
        # Carregar SVGs para os ícones
        icons_dir = os.path.abspath("assets/icons")
        
        # Dentro do método render, após carregar o rodapé:
        rodape_path = os.path.join(icons_dir, "rodape.png")
        try:
            with open(rodape_path, "rb") as f:
                icon_bytes = f.read()
                logger.info(f"Arquivo rodapé lido com sucesso: {rodape_path}, tamanho: {len(icon_bytes)} bytes")
                icon_rodape = base64.b64encode(icon_bytes).decode("ascii")
                logger.info(f"Base64 do rodapé gerado com sucesso, tamanho: {len(icon_rodape)}")
        except Exception as e:
            logger.error(f"Erro ao carregar rodapé: {str(e)}")
            icon_rodape = ""  # Valor padrão vazio em caso de erro
        
        # Setas (carregar como base64)
        seta_up_verde_path = os.path.join(icons_dir, "SETA-UP-VERDE.svg")
        with open(seta_up_verde_path, "rb") as f:
            seta_up_verde_b64 = base64.b64encode(f.read()).decode("utf-8")
        
        seta_down_laranja_path = os.path.join(icons_dir, "SETA-DOWN-LARANJA.svg")
        with open(seta_down_laranja_path, "rb") as f:
            seta_down_laranja_b64 = base64.b64encode(f.read()).decode("utf-8")
            
        seta_up_laranja_path = os.path.join(icons_dir, "SETA-UP-LARANJA.svg")
        with open(seta_up_laranja_path, "rb") as f:
            seta_up_laranja_b64 = base64.b64encode(f.read()).decode("utf-8")
            
        seta_down_verde_path = os.path.join(icons_dir, "SETA-DOWN-VERDE.svg")
        with open(seta_down_verde_path, "rb") as f:
            seta_down_verde_b64 = base64.b64encode(f.read()).decode("utf-8")
        
        # Processar dados do relatório
        lucro_operacional_data = next((item for item in relatorio_data if item['categoria'] == 'Lucro Operacional'), {})
        investimentos_data = next((item for item in relatorio_data if item['categoria'] == 'Investimentos'), {})

        # Receita total para cálculos
        receita_total = next(
            (subcat['valor'] for subcat in lucro_operacional_data.get('subcategorias', []) if subcat['subcategoria'] == 'Receita'), 
            0
        )
        
        # Lucro Operacional
        lucro_operacional_categories = []
        lucro_operacional_total = lucro_operacional_data.get('valor', 0)
        lucro_operacional_av = lucro_operacional_data.get('av_categoria', 0)
        
        for subcat in lucro_operacional_data.get('subcategorias', []):
            lucro_operacional_categories.append({
                "name": subcat['subcategoria'],
                "value": abs(subcat['valor']),
                "representatividade": abs(subcat['av']),
                "variacao": subcat['ah'],
                "barra_rep": abs(subcat['representatividade'])
            })

        # Investimentos
        investimentos_categories = []
        investimentos_total = abs(investimentos_data.get('valor', 0))
        investimentos_av = investimentos_data.get('av_categoria', 0)
        
        for subcat in investimentos_data.get('subcategorias', []):
            investimentos_categories.append({
                "name": subcat['subcategoria'],
                "value": abs(subcat['valor']),
                "representatividade": abs(subcat['av']),
                "variacao": subcat['ah'],
                "barra_rep": abs(subcat['representatividade'])
            })

        # Dados para o template
        template_data = {
            "nome": cliente_nome,
            "Periodo": f"{mes_nome}/{ano}",
            "notas": notas,
            "lucro_operacional": lucro_operacional_total,
            "represent_lucro_operacional": abs(lucro_operacional_av) or 0,
            "lucro_operacional_categories": lucro_operacional_categories,
            "investimentos": investimentos_total,
            "represent_investimentos": abs(investimentos_av) or 0,
            "investimentos_categories": investimentos_categories
        }
        
        # Renderizar template
        return self.template.render(
            data=template_data,
            icon_rodape=icon_rodape,
            seta_b64=seta_up_verde_b64,
            seta_b64_2=seta_down_laranja_b64,
            seta_b64_3=seta_up_laranja_b64,
            seta_b64_4=seta_down_verde_b64,
            cliente_nome=cliente_nome,
            mes_nome=mes_nome,
            ano=ano
        )