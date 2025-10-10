"""
Finalizador de PDFs - Aplica pós-processamento aos PDFs gerados.

Este módulo integra o pós-processamento de PDFs ao pipeline principal,
removendo automaticamente páginas em branco dos relatórios gerados.
"""

import os
import sys
import logging
from typing import Optional, Tuple

# Adicionar o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.pdf_postprocessor import PDFPostProcessor

logger = logging.getLogger(__name__)


class PDFinalizer:
    """
    Classe responsável por finalizar e otimizar PDFs gerados.
    
    Aplica pós-processamento para:
    - Remover páginas em branco
    - Otimizar estrutura do PDF  
    - Gerar logs de análise
    """
    
    def __init__(self):
        self.postprocessor = PDFPostProcessor()
    
    def finalize_pdf(self, pdf_path: str, remove_blank_pages: bool = True) -> Tuple[bool, str, list]:
        """
        Finaliza um PDF aplicando otimizações.
        
        Args:
            pdf_path: Caminho do PDF original
            remove_blank_pages: Se deve remover páginas em branco
            
        Returns:
            Tupla (success, final_path, removed_pages)
        """
        if not os.path.exists(pdf_path):
            logger.error(f"PDF não encontrado: {pdf_path}")
            return False, pdf_path, []
        
        logger.info(f"🔧 Finalizando PDF: {os.path.basename(pdf_path)}")
        
        try:
            # Análise inicial
            stats_before = PDFPostProcessor.analyze_pdf_content(pdf_path)
            logger.info(f"📊 PDF original: {stats_before['total_pages']} páginas")
            
            if stats_before['empty_pages']:
                logger.warning(f"❌ Páginas vazias detectadas: {stats_before['empty_pages']}")
            
            # Aplicar pós-processamento se necessário
            if remove_blank_pages and stats_before['empty_pages']:
                success, final_path, removed_pages = self.postprocessor.remove_blank_pages(pdf_path)
                
                if success:
                    # Substituir arquivo original pelo corrigido
                    if final_path != pdf_path:
                        import shutil
                        backup_path = pdf_path + ".backup"
                        shutil.move(pdf_path, backup_path)
                        shutil.move(final_path, pdf_path)
                        os.remove(backup_path)
                        logger.info(f"✅ PDF corrigido salvo como: {os.path.basename(pdf_path)}")
                    
                    return True, pdf_path, removed_pages
                else:
                    logger.warning("⚠️  Falha no pós-processamento, mantendo PDF original")
                    return False, pdf_path, []
            else:
                # Nenhum processamento necessário
                logger.info("✅ PDF já está otimizado")
                return True, pdf_path, []
                
        except Exception as e:
            logger.error(f"❌ Erro ao finalizar PDF: {e}")
            return False, pdf_path, []
    
    def analyze_pdf(self, pdf_path: str) -> Optional[dict]:
        """
        Analisa um PDF e retorna estatísticas detalhadas.
        
        Args:
            pdf_path: Caminho do PDF
            
        Returns:
            Dicionário com estatísticas ou None se erro
        """
        try:
            return PDFPostProcessor.analyze_pdf_content(pdf_path)
        except Exception as e:
            logger.error(f"❌ Erro ao analisar PDF: {e}")
            return None


def test_pdf_finalizer():
    """Função de teste para o finalizador."""
    # Teste com o PDF do Cliente 235
    pdf_path = r"c:\Users\usuario\Downloads\Relatorio_Cliente_235_Setembro_2025 (4).pdf"
    
    if os.path.exists(pdf_path):
        print("🧪 Testando finalizador de PDF...")
        
        finalizer = PDFinalizer()
        
        # Fazer uma cópia para teste
        import shutil
        test_path = pdf_path.replace(".pdf", "_TEST.pdf")
        shutil.copy2(pdf_path, test_path)
        
        # Finalizar
        success, final_path, removed_pages = finalizer.finalize_pdf(test_path)
        
        if success:
            print(f"✅ PDF finalizado com sucesso!")
            print(f"📋 Páginas removidas: {removed_pages}")
            print(f"📁 Arquivo final: {os.path.basename(final_path)}")
        else:
            print("❌ Falha na finalização")
    else:
        print(f"❌ PDF de teste não encontrado: {pdf_path}")


if __name__ == "__main__":
    # Configurar logging para teste
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    test_pdf_finalizer()