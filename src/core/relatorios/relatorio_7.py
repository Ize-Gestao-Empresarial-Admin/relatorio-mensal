# src/core/relatorios/relatorio_7.py
import os
from datetime import date
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Relatorio7:
    def __init__(self, indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..", "static"))
        logger.info(f"Diretório base para imagens: {self.base_dir}")

    def gerar_relatorio(self, mes_atual: date, mes_anterior: Optional[date] = None) -> dict:
        """Gera o relatório com imagens estáticas."""
        imagem1 = os.path.join(self.base_dir, "relatorio_7_p1.PNG")
        imagem2 = os.path.join(self.base_dir, "relatorio_7_p2.PNG")
        
        # Verificar se as imagens existem
        if not os.path.exists(imagem1):
            logger.warning(f"Imagem não encontrada: {imagem1}")
        if not os.path.exists(imagem2):
            logger.warning(f"Imagem não encontrada: {imagem2}")
        
        return {
            "Empresa": self.nome_cliente,
            "Imagens": [imagem1, imagem2]
        }