from typing import Dict, Optional
from src.rendering.renderers.base_renderer import BaseRenderer
from src.rendering.renderers.relatorio1_renderer import Relatorio1Renderer
from src.rendering.renderers.relatorio2_renderer import Relatorio2Renderer
from src.rendering.renderers.relatorio3_renderer import Relatorio3Renderer
#from src.rendering.renderers.relatorio4_renderer import Relatorio1Renderer
#from src.rendering.renderers.relatorio5_renderer import Relatorio1Renderer
#from src.rendering.renderers.relatorio5_renderer import Relatorio1Renderer
from src.rendering.renderers.relatorio7_renderer import Relatorio7Renderer

# Dicionário de renderizadores disponíveis
_RENDERERS: Dict[int, BaseRenderer] = {
    1: Relatorio1Renderer(),
    2: Relatorio2Renderer(),
    3: Relatorio3Renderer(),
    7: Relatorio7Renderer()
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