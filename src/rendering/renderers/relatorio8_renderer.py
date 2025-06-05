from typing import Dict, Any, List, Tuple, Union
from src.rendering.renderers.base_renderer import BaseRenderer
import os
import base64
import logging
logger = logging.getLogger(__name__)

class Relatorio8Renderer(BaseRenderer):
    """Renderizador para o Relatório 8 - Nota do Consultor."""

    def render(
        self,
        data: Union[List, Tuple[List, Dict[str, Any]]], 
        cliente_nome: str,
        mes_nome: str,
        ano: int
    ) -> str:
        """
        Renderiza os dados do Relatório 8 em HTML.

        Args:
            data: Dados do relatório (tupla com lista vazia e dicionário com nota_consultor).
            cliente_nome: Nome do cliente.
            mes_nome: Nome do mês.
            ano: Ano do relatório.

        Returns:
            HTML formatado.
        """
        
        # Carregar ícones e imagens
        icons_dir = os.path.abspath("assets/icons")
        
        # Rodapé - mesmo padrão do relatório 4
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
        
        # Extrair dados
        if isinstance(data, tuple) and len(data) == 2:
            _, notas = data
            nota_consultor = notas.get("nota_consultor", "<p>Nenhuma nota fornecida.</p>")
        else:
            nota_consultor = "<p>Nenhuma nota fornecida.</p>"

        # Dados para o template
        template_data = {
            "nome": cliente_nome,
            "Periodo": f"{mes_nome}/{ano}",
            "nota_consultor": nota_consultor
        }

        # Carregar template
        template = self.env.get_template("relatorio8/template.html")
        return template.render(
            data=template_data,
            icon_rodape=icon_rodape,  # Usando a variável icon_rodape em vez de logo_svg
            cliente_nome=cliente_nome,
            mes_nome=mes_nome,
            ano=ano
        )
