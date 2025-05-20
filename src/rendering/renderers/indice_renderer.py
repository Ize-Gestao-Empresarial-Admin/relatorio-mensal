# src/rendering/renderers/indice_renderer.py
from typing import Dict, Any
from .base_renderer import BaseRenderer
import os

class IndiceRenderer(BaseRenderer):
    def __init__(self):
        super().__init__()
        # Carregar o template do índice
        self.template = self.env.get_template("indice/template.html")
        # Carregar o logo SVG (ajuste o caminho conforme necessário)
        logo_path = os.path.join("assets", "icons", "IZE-LOGO-1.svg")
        with open(logo_path, "r", encoding="utf-8") as f:
            self.logo_svg = f.read()

    def render(self, data: Dict[str, Any], cliente_nome: str, mes_nome: str, ano: int) -> str:
        """
        Renderiza o índice em HTML com base nos dados fornecidos.

        Args:
            data: Dicionário com as informações do índice (indice_data).
            cliente_nome: Nome do cliente (não usado diretamente, pois está em data).
            mes_nome: Nome do mês (não usado diretamente, pois está em data).
            ano: Ano do relatório (não usado diretamente, pois está em data).

        Returns:
            String com o HTML renderizado.
        """
        return self.template.render(data=data, logo_svg=self.logo_svg)