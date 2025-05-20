from typing import Dict, Any, List, Tuple, Union
from src.rendering.renderers.base_renderer import BaseRenderer
import os
import base64

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
        
        # Carregar SVGs para os ícones
        icons_dir = os.path.abspath("assets/icons")
        
        # Logo
        logo_path = os.path.join(icons_dir, "IZE-LOGO-2.svg")
        with open(logo_path, "r", encoding="utf-8") as f:
            logo_svg = f.read()
        
        # Extrair dados
        if isinstance(data, tuple) and len(data) == 2:
            _, notas = data
            nota_consultor = notas.get("nota_consultor", "<p>Nenhuma nota fornecida.</p>")
        else:
            nota_consultor = "<p>Nenhuma nota fornecida.</p>"

        # Carregar logo
        icons_dir = os.path.abspath("assets/icons")
        logo_path = os.path.join(icons_dir, "IZE-LOGO-2.svg")
        with open(logo_path, "r", encoding="utf-8") as f:
            logo_svg = f.read()

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
            logo_svg=logo_svg,
            cliente_nome=cliente_nome,
            mes_nome=mes_nome,
            ano=ano
        )
