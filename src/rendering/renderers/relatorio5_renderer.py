from typing import Dict, Any, List, Tuple, Union
from src.rendering.renderers.base_renderer import BaseRenderer
import os
import base64
import logging

logger = logging.getLogger(__name__)

class Relatorio5Renderer(BaseRenderer):
    """Renderizador específico para o Relatório 5 - Geração de Caixa"""
    
    def __init__(self):
        super().__init__()
        # Carregar o template do relatório 5
        self.template = self.env.get_template("relatorio5/template.html")
    
    def render(self, data: Union[List[Dict[str, Any]], Tuple[List[Dict[str, Any]], Dict[str, str]]], 
               cliente_nome: str, mes_nome: str, ano: int) -> str:
        """
        Renderiza os dados do Relatório 5 em HTML.

        Args:
            data: Lista de dados do relatório ou tupla com dados e notas.
            cliente_nome: Nome do cliente.
            mes_nome: Nome do mês.
            ano: Ano do relatório.

        Returns:
            HTML formatado.
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
        
        # Carregar rodapé
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
            
        # Processar dados do relatório
        geracao_de_caixa_data = next((item for item in relatorio_data if item['categoria'] == 'Geração de Caixa'), {})
        
        # Geração de Caixa
        geracao_de_caixa_categories = []
        geracao_de_caixa_total = geracao_de_caixa_data.get('valor', 0)
        geracao_de_caixa_av = geracao_de_caixa_data.get('av_categoria', 0)
        
        for subcat in geracao_de_caixa_data.get('subcategorias', []):
            geracao_de_caixa_categories.append({
                "name": subcat['subcategoria'],
                "value": subcat['valor'],
                "representatividade": abs(subcat['av']),
                "variacao": subcat['ah'],
                "barra_rep": abs(subcat['representatividade'])  # Usar a representatividade fornecida
            })

        # Dados para o template
        template_data = {
            "nome": cliente_nome,
            "Periodo": f"{mes_nome}/{ano}",
            "notas": notas,
            "geracao_de_caixa": geracao_de_caixa_total,
            "represent_geracao_de_caixa": abs(geracao_de_caixa_av) or 0,
            "geracao_de_caixa_categories": geracao_de_caixa_categories
        }
        
        # Renderizar o template
        return self.template.render(
            data=template_data,
            icon_rodape=icon_rodape,
            seta_b64=seta_up_verde_b64,
            seta_b64_2=seta_down_laranja_b64,
            cliente_nome=cliente_nome,
            mes_nome=mes_nome,
            ano=ano
        )