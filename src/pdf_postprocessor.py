#!/usr/bin/env python3
"""
Utilitário para pós-processamento de PDFs - Remove páginas vazias automaticamente.
"""

import PyPDF2
import logging
import os
from typing import List, Tuple

logger = logging.getLogger(__name__)

class PDFPostProcessor:
    """Classe para pós-processamento de PDFs gerados."""
    
    @staticmethod
    def remove_blank_pages(pdf_path: str, output_path: str = None) -> Tuple[bool, str, List[int]]:
        """
        Remove páginas vazias de um PDF e salva o resultado.
        
        Args:
            pdf_path: Caminho do PDF original
            output_path: Caminho do PDF de saída (se None, sobrescreve o original)
            
        Returns:
            Tupla (sucesso, caminho_final, paginas_removidas)
        """
        if output_path is None:
            output_path = pdf_path
            
        blank_pages = []
        total_pages = 0
        
        try:
            with open(pdf_path, 'rb') as input_file:
                reader = PyPDF2.PdfReader(input_file)
                writer = PyPDF2.PdfWriter()
                total_pages = len(reader.pages)
                
                logger.info(f"📄 Analisando PDF: {pdf_path} ({total_pages} páginas)")
                
                for page_num, page in enumerate(reader.pages, 1):
                    # Extrair texto da página
                    try:
                        text = page.extract_text().strip()
                        text_length = len(text)
                        
                        # Verificar se tem imagens/objetos
                        has_images = False
                        has_resources = False
                        try:
                            resources = page.get('/Resources', {})
                            if isinstance(resources, dict):
                                has_images = '/XObject' in resources
                                has_resources = any(key in resources for key in ['/XObject', '/Font', '/ColorSpace', '/ExtGState'])
                        except:
                            has_images = False
                            has_resources = False
                        
                        # CRITÉRIO MAIS PERMISSIVO: Só remove se REALMENTE vazio
                        # - Sem texto E sem imagens E sem recursos visuais
                        should_keep = (
                            text_length > 0 or  # Tem algum texto
                            has_images or       # Tem imagens/gráficos
                            has_resources       # Tem recursos visuais (fontes, etc)
                        )
                        
                        if should_keep:
                            writer.add_page(page)
                            if text_length > 50:
                                logger.debug(f"✅ Página {page_num}: OK ({text_length} chars)")
                            else:
                                logger.debug(f"✅ Página {page_num}: OK ({text_length} chars, recursos: {has_resources}, imagens: {has_images})")
                        else:
                            # Página realmente vazia - SEM texto, SEM imagens, SEM recursos
                            blank_pages.append(page_num)
                            logger.warning(f"❌ Página {page_num}: REMOVIDA (completamente vazia - {text_length} chars, imagens: {has_images}, recursos: {has_resources})")
                                
                    except Exception as e:
                        # Em caso de erro, manter a página por segurança
                        writer.add_page(page)
                        logger.warning(f"⚠️  Página {page_num}: Erro ao analisar, mantida: {e}")
                
                # Salvar apenas se há páginas para salvar
                if len(writer.pages) > 0:
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    pages_kept = len(writer.pages)
                    pages_removed = len(blank_pages)
                    
                    logger.info(f"🎯 PDF pós-processado: {pages_kept} páginas mantidas, {pages_removed} removidas")
                    
                    if blank_pages:
                        logger.info(f"📋 Páginas removidas: {blank_pages}")
                    
                    return True, output_path, blank_pages
                else:
                    logger.error(f"❌ Erro: PDF ficaria vazio após remoção")
                    return False, pdf_path, blank_pages
                    
        except Exception as e:
            logger.error(f"❌ Erro ao processar PDF {pdf_path}: {e}")
            return False, pdf_path, []
    
    @staticmethod
    def analyze_pdf_content(pdf_path: str) -> dict:
        """
        Analisa o conteúdo de um PDF e retorna estatísticas.
        
        Args:
            pdf_path: Caminho do PDF
            
        Returns:
            Dicionário com estatísticas do PDF
        """
        stats = {
            'total_pages': 0,
            'empty_pages': [],
            'suspicious_pages': [],  # Páginas com pouco conteúdo
            'good_pages': [],
            'error_pages': []
        }
        
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                stats['total_pages'] = len(reader.pages)
                
                for page_num, page in enumerate(reader.pages, 1):
                    try:
                        text = page.extract_text().strip()
                        text_length = len(text)
                        
                        # Verificar recursos visuais também
                        has_resources = False
                        try:
                            resources = page.get('/Resources', {})
                            if isinstance(resources, dict):
                                has_resources = any(key in resources for key in ['/XObject', '/Font', '/ColorSpace', '/ExtGState'])
                        except:
                            has_resources = False
                            
                        if text_length == 0 and not has_resources:
                            stats['empty_pages'].append(page_num)
                        elif text_length < 20 and not has_resources:
                            stats['suspicious_pages'].append(page_num)
                        else:
                            stats['good_pages'].append(page_num)
                            
                    except Exception as e:
                        stats['error_pages'].append(page_num)
                        logger.warning(f"Erro ao analisar página {page_num}: {e}")
                        
        except Exception as e:
            logger.error(f"Erro ao analisar PDF {pdf_path}: {e}")
            
        return stats


def test_pdf_postprocessor():
    """Função de teste para o pós-processador."""
    # Teste com o PDF do Cliente 235
    pdf_path = r"c:\Users\usuario\Downloads\Relatorio_Cliente_235_Setembro_2025 (4).pdf"
    
    if os.path.exists(pdf_path):
        print("🧪 Testando pós-processador de PDF...")
        
        # Analisar antes
        stats_before = PDFPostProcessor.analyze_pdf_content(pdf_path)
        print(f"📊 Antes: {stats_before['total_pages']} páginas")
        print(f"❌ Páginas vazias: {stats_before['empty_pages']}")
        print(f"⚠️  Páginas suspeitas: {stats_before['suspicious_pages']}")
        
        # Processar
        output_path = pdf_path.replace('.pdf', '_FIXED.pdf')
        success, final_path, removed_pages = PDFPostProcessor.remove_blank_pages(pdf_path, output_path)
        
        if success:
            print(f"✅ PDF processado com sucesso: {final_path}")
            print(f"📋 Páginas removidas: {removed_pages}")
            
            # Analisar depois
            stats_after = PDFPostProcessor.analyze_pdf_content(final_path)
            print(f"📊 Depois: {stats_after['total_pages']} páginas")
            print(f"❌ Páginas vazias: {stats_after['empty_pages']}")
        else:
            print("❌ Falha no processamento")
    else:
        print(f"❌ PDF não encontrado: {pdf_path}")


if __name__ == "__main__":
    test_pdf_postprocessor()