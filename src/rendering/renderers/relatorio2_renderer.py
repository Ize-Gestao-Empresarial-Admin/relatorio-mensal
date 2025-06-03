# src/rendering/renderers/relatorio2_renderer.py
from typing import Dict, Any, List, Tuple, Union
from src.rendering.renderers.base_renderer import BaseRenderer
import os
import base64
import logging
logger = logging.getLogger(__name__)

class Relatorio2Renderer(BaseRenderer):
    """
    Renderizador para o Relatório 2 - Análise de Fluxo de Caixa 2.
    Converte os dados do relatório em HTML para posterior geração de PDF.
    """
    
    def __init__(self):
        super().__init__()
        # Carregar o template do relatório 2
        self.template = self.env.get_template("relatorio2/template.html")

    def render(self, data: Union[List[Dict[str, Any]], Tuple[List[Dict[str, Any]], Dict[str, str]]], 
               cliente_nome: str, mes_nome: str, ano: int) -> str:
        """
        Renderiza os dados do Relatório 2 em HTML.
        
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
        lucro_bruto_data = next((item for item in relatorio_data if item['categoria'] == 'Lucro Bruto'), {})
        despesas_fixas_data = next((item for item in relatorio_data if item['categoria'] == 'Despesas Fixas'), {})

        # Lucro Bruto
        lucro_bruto_categories = []
        lucro_bruto_total = lucro_bruto_data.get('valor', 0)
        lucro_bruto_av = lucro_bruto_data.get('av_categoria', 0)
        
        # Receita total para cálculos
        receita_total = next(
            (subcat['valor'] for subcat in lucro_bruto_data.get('subcategorias', []) if subcat['subcategoria'] == 'Receita'), 
            0
        )
        
        # Adiciona subcategorias de Lucro Bruto
        for subcat in lucro_bruto_data.get('subcategorias', []):
            lucro_bruto_categories.append({
                "name": subcat['subcategoria'],
                "value": abs(subcat['valor']),
                "representatividade": abs(subcat['av']),
                "variacao": subcat['ah'],
                "barra_rep": subcat['representatividade']
            })

        # Despesas Fixas
        despesas_fixas_categories = []
        despesas_fixas_total = abs(despesas_fixas_data.get('valor', 0))
        despesas_fixas_av = despesas_fixas_data.get('av_categoria', 0)
        
        # Adiciona subcategorias de Despesas Fixas
        for subcat in despesas_fixas_data.get('subcategorias', []):
            despesas_fixas_categories.append({
                "name": subcat['subcategoria'],
                "value": abs(subcat['valor']),
                "representatividade": abs(subcat['av']),
                "variacao": subcat['ah'],
                "barra_rep": subcat['representatividade']
            })

        # Dados para o template
        template_data = {
            "nome": cliente_nome,
            "Periodo": f"{mes_nome}/{ano}",
            "notas": notas,
            "lucro_bruto": lucro_bruto_total,
            "represent_lucro_bruto": abs(lucro_bruto_av) or 0,
            "lucro_bruto_categories": lucro_bruto_categories,
            "despesas_fixas": despesas_fixas_total,
            "represent_despesas_fixas": abs(despesas_fixas_av) or 0,
            "despesas_fixas_categories": despesas_fixas_categories
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