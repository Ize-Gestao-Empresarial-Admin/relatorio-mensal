#src/rendering/renderers/relatorio1_renderer.py
from typing import Dict, Any, List, Tuple, Union
from src.rendering.renderers.base_renderer import BaseRenderer
import os
import base64
import logging
logger = logging.getLogger(__name__)

class Relatorio1Renderer(BaseRenderer):
    """
    Renderizador para o Relatório 1 - Análise do Fluxo de Caixa.
    Converte os dados do relatório em HTML para posterior geração de PDF.
    """
    
    def __init__(self):
        super().__init__()
        # Carregar o template do relatório 1
        self.template = self.env.get_template("relatorio1/template.html")

    def render(self, data: Union[List[Dict[str, Any]], Tuple[List[Dict[str, Any]], Dict[str, str]]], 
               cliente_nome: str, mes_nome: str, ano: int) -> str:
        """
        Renderiza os dados do Relatório 1 em HTML.
        
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
        
        # Rodapé
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
        # Estrutura: [{'categoria': 'Receitas', 'valor': X, 'subcategorias': [...]}, {'categoria': 'Custos Variáveis', ...}]
        receitas_data = next((item for item in relatorio_data if item['categoria'] == 'Receitas'), {})
        custos_data = next((item for item in relatorio_data if item['categoria'] == 'Custos Variáveis'), {})

        # Receitas
        receita_categories = []
        receita_total = receitas_data.get('valor', 0)
        receita_subcategorias_sum = sum(subcat['valor'] for subcat in receitas_data.get('subcategorias', []))
        receita_restante = max(0, receita_total - receita_subcategorias_sum)

        for subcat in receitas_data.get('subcategorias', []):
            receita_categories.append({
                "name": subcat['subcategoria'],
                "value": subcat['valor'],
                "representatividade": subcat['av'],
                "variacao": subcat['ah'],
                "barra_rep": round((subcat['valor'] / receita_total) * 100, 2) if receita_total != 0 else 0
            })

        # Custos Variáveis
        custo_categories = []
        custos_total = custos_data.get('valor', 0)
        custos_subcategorias_sum = sum(abs(subcat['valor']) for subcat in custos_data.get('subcategorias', []))
        custos_restante = max(0, abs(custos_total) - custos_subcategorias_sum)
        
        total_rep = sum(abs(subcat['representatividade']) for subcat in custos_data.get('subcategorias', []))
        
        for i, subcat in enumerate(custos_data.get('subcategorias', [])):
            rep = abs(subcat['representatividade'])
            barra_rep = round((rep / total_rep * 100) if total_rep > 0 else 0, 2)
            
            if i == len(custos_data.get('subcategorias', [])) - 1:
                soma_atual = sum(c['barra_rep'] for c in custo_categories)
                barra_rep = round(100 - soma_atual, 2) if soma_atual < 100 else barra_rep
            
            custo_categories.append({
                "name": subcat['subcategoria'],
                "value": abs(subcat['valor']),
                "representatividade": abs(subcat['av']),  # ALTERADO: usar AV em vez de rep
                "variacao": subcat['ah'],
                "barra_rep": barra_rep 
            })

        # Dados para o template
        template_data = {
            "nome": cliente_nome,
            "Periodo": f"{mes_nome}/{ano}",
            "notas": notas,
            "receita": receitas_data.get('valor', 0),
            "represent_receita": 100.0,
            "receita_categories": receita_categories,
            "custos": abs(custos_data.get('valor') or 0),
            "represent_custos": abs(custos_data.get('valor') or 0) / (receitas_data.get('valor') or 1) * 100 if (receitas_data.get('valor') or 0) > 0 else 0,
            "custo_categories": custo_categories
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