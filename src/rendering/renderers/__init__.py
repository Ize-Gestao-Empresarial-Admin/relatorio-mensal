#src/rendering/renderers/__init__.py
from typing import Dict, Optional
from src.rendering.renderers.base_renderer import BaseRenderer
from .indice_renderer import IndiceRenderer
from src.rendering.renderers.relatorio1_renderer import Relatorio1Renderer
from src.rendering.renderers.relatorio2_renderer import Relatorio2Renderer
from src.rendering.renderers.relatorio3_renderer import Relatorio3Renderer
from src.rendering.renderers.relatorio4_renderer import Relatorio4Renderer
from src.rendering.renderers.relatorio5_renderer import Relatorio5Renderer
from src.rendering.renderers.relatorio6_renderer import Relatorio6Renderer
from src.rendering.renderers.relatorio7_renderer import Relatorio7Renderer
from src.rendering.renderers.relatorio8_renderer import Relatorio8Renderer


# Dicionário de renderizadores disponíveis
_RENDERERS: Dict[int, BaseRenderer] = {
    0: IndiceRenderer(),
    1: Relatorio1Renderer(),
    2: Relatorio2Renderer(),
    3: Relatorio3Renderer(),
    4: Relatorio4Renderer(),
    5: Relatorio5Renderer(),
    6: Relatorio6Renderer(),
    7: Relatorio7Renderer(),
    8: Relatorio8Renderer(),
}


def get_renderer(relatorio_num: int) -> Optional[BaseRenderer]:
    """
    Retorna o renderizador apropriado para o número do relatório.
    
    Args:
        relatorio_num: Número do relatório (1-7)
        
    Returns:
        Instância do renderizador ou None se não encontrado
    """
    return _RENDERERS.get(relatorio_num)