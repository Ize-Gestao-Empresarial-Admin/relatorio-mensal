# src/rendering/renderers/indice_renderer.py
from typing import Dict, Any
from .base_renderer import BaseRenderer
import os
import base64

class IndiceRenderer(BaseRenderer):
    def __init__(self):
        super().__init__()
        # Carregar o template do índice
        self.template = self.env.get_template("indice/template.html")
        
        # Carregar ícones e imagens
        icons_dir = os.path.abspath("assets/icons")
        
        # Carregar o logo PNG
        logo_path = os.path.join(icons_dir, "IZE-SIMBOLO-1.png")
        try:
            with open(logo_path, "rb") as f:
                logo_bytes = f.read()
                self.logo_png_b64 = base64.b64encode(logo_bytes).decode("ascii")
        except Exception as e:
            print(f"Erro ao carregar logo: {str(e)}")
            self.logo_png_b64 = ""

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
        return self.template.render(data=data, logo_png_b64=self.logo_png_b64)