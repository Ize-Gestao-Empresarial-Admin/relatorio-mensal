#!/usr/bin/env python3
"""
Utilitário para pós-processamento de PDFs - Remove páginas vazias automaticamente.
"""

import PyPDF2
import logging
import os
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)

class PDFPostProcessor:
    """Classe para pós-processamento de PDFs gerados."""
    
    @staticmethod
    def remove_blank_pages(pdf_path: str, output_path: str = None) -> Tuple[bool, str, List[int]]:
        """
        Remove páginas vazias de um PDF e salva o resultado.
        ALGORITMO INTELIGENTE: Ignora rodapés padrão e detecta páginas realmente vazias.
        
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
                    try:
                        # Extrair texto completo da página
                        raw_text = page.extract_text()
                        text = raw_text.strip() if raw_text else ""
                        text_length = len(text)
                        
                        # Analisar recursos da página
                        page_analysis = PDFPostProcessor._analyze_page_content(page, text)
                        
                        # LÓGICA INTELIGENTE para detectar páginas realmente vazias
                        is_truly_empty = PDFPostProcessor._is_page_truly_empty(
                            text, page_analysis, page_num, total_pages
                        )
                        
                        if not is_truly_empty:
                            # Página tem conteúdo - manter
                            writer.add_page(page)
                            
                            # Log detalhado para debug
                            content_summary = []
                            if page_analysis['meaningful_text_length'] > 0:
                                content_summary.append(f"{page_analysis['meaningful_text_length']} chars úteis")
                            if page_analysis['has_images']:
                                content_summary.append("imagens")
                            if page_analysis['has_charts']:
                                content_summary.append("gráficos")
                            if page_analysis['has_visual_elements']:
                                content_summary.append("elementos visuais")
                            
                            logger.debug(f"✅ Página {page_num}: OK ({', '.join(content_summary) if content_summary else 'rodapé apenas'})")
                        else:
                            # Página realmente vazia - apenas rodapé
                            blank_pages.append(page_num)
                            logger.warning(f"❌ Página {page_num}: REMOVIDA (apenas rodapé - {text_length} chars totais, {page_analysis['meaningful_text_length']} chars úteis)")
                                
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
    def _analyze_page_content(page, text: str) -> dict:
        """
        Analisa o conteúdo de uma página de forma inteligente.
        
        Returns:
            Dict com análise detalhada da página
        """
        analysis = {
            'has_images': False,
            'has_charts': False,
            'has_visual_elements': False,
            'meaningful_text_length': 0,
            'footer_patterns': [],
            'is_special_page': False
        }
        
        try:
            # Verificar recursos visuais
            resources = page.get('/Resources', {})
            if isinstance(resources, dict):
                analysis['has_images'] = '/XObject' in resources
                analysis['has_visual_elements'] = any(key in resources for key in ['/XObject', '/Font', '/ColorSpace', '/ExtGState'])
                
                # Detectar possíveis gráficos (recursos mais complexos)
                if '/XObject' in resources:
                    xobjects = resources.get('/XObject', {})
                    if isinstance(xobjects, dict) and len(xobjects) > 1:
                        analysis['has_charts'] = True
        except:
            pass
        
        # Analisar texto ignorando padrões de rodapé
        if text:
            # Padrões comuns de rodapé (ajustar conforme necessário)
            footer_patterns = [
                r'ize\.com\.br',
                r'@ize_',
                r'\d{2}/\d{2}/\d{4}',  # datas
                r'página\s+\d+',
                r'relatório\s+mensal',
                r'www\.',
                r'contato@',
                r'instagram\.com',
                r'facebook\.com',
                r'linkedin\.com'
            ]
            
            import re
            text_without_footer = text
            
            for pattern in footer_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                analysis['footer_patterns'].extend(matches)
                text_without_footer = re.sub(pattern, '', text_without_footer, flags=re.IGNORECASE)
            
            # Remover caracteres especiais e espaços em excesso
            meaningful_text = re.sub(r'[^\w\s]', ' ', text_without_footer)
            meaningful_text = re.sub(r'\s+', ' ', meaningful_text).strip()
            
            analysis['meaningful_text_length'] = len(meaningful_text)
        
        return analysis
    
    @staticmethod
    def _is_page_truly_empty(text: str, analysis: dict, page_num: int, total_pages: int) -> bool:
        """
        Determina se uma página está realmente vazia (apenas rodapé).
        
        Args:
            text: Texto completo da página
            analysis: Análise da página do _analyze_page_content
            page_num: Número da página
            total_pages: Total de páginas
            
        Returns:
            True se a página está realmente vazia (apenas rodapé)
        """
        # Páginas especiais nunca remover (primeira, últimas 2)
        if page_num == 1 or page_num >= total_pages - 1:
            return False
        
        # Se tem elementos visuais significativos, não está vazia
        if analysis['has_images'] or analysis['has_charts']:
            return False
        
        # Se tem texto significativo (mais que apenas rodapé), não está vazia
        if analysis['meaningful_text_length'] > 20:  # Threshold conservador
            return False
        
        # Se tem recursos visuais avançados, não está vazia
        if analysis['has_visual_elements'] and analysis['meaningful_text_length'] > 5:
            return False
        
        # Se chegou até aqui, provavelmente é só rodapé
        total_text_length = len(text.strip())
        
        # Se tem muito texto mesmo com pouco texto "útil", é suspeito - manter
        if total_text_length > 100 and analysis['meaningful_text_length'] > 0:
            return False
        
        # Página realmente vazia ou apenas com rodapé
        return True
    
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
                        raw_text = page.extract_text()
                        text = raw_text.strip() if raw_text else ""
                        
                        # Usar a nova análise inteligente
                        page_analysis = PDFPostProcessor._analyze_page_content(page, text)
                        is_empty = PDFPostProcessor._is_page_truly_empty(text, page_analysis, page_num, stats['total_pages'])
                        
                        if is_empty:
                            stats['empty_pages'].append(page_num)
                        elif page_analysis['meaningful_text_length'] < 50 and not page_analysis['has_visual_elements']:
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
    """Função de teste melhorada para o pós-processador."""
    # Buscar PDFs na pasta outputs
    import glob
    pdf_files = glob.glob("outputs/*.pdf")
    
    if not pdf_files:
        print("❌ Nenhum PDF encontrado na pasta outputs/")
        return
    
    # Usar o PDF mais recente
    pdf_path = max(pdf_files, key=os.path.getctime)
    print(f"🧪 Testando pós-processador com: {os.path.basename(pdf_path)}")
    
    # Analisar antes
    stats_before = PDFPostProcessor.analyze_pdf_content(pdf_path)
    print(f"\n📊 ANÁLISE INICIAL:")
    print(f"  Total: {stats_before['total_pages']} páginas")
    print(f"  ❌ Vazias: {stats_before['empty_pages']}")
    print(f"  ⚠️  Suspeitas: {stats_before['suspicious_pages']}")
    print(f"  ✅ Boas: {stats_before['good_pages']}")
    
    if stats_before['empty_pages']:
        print(f"\n🔧 Processando remoção de {len(stats_before['empty_pages'])} páginas vazias...")
        
        # Fazer cópia para teste
        output_path = pdf_path.replace('.pdf', '_PROCESSADO.pdf')
        success, final_path, removed_pages = PDFPostProcessor.remove_blank_pages(pdf_path, output_path)
        
        if success:
            print(f"✅ PDF processado: {os.path.basename(final_path)}")
            print(f"📋 Páginas removidas: {removed_pages}")
            
            # Analisar depois
            stats_after = PDFPostProcessor.analyze_pdf_content(final_path)
            print(f"\n📊 ANÁLISE FINAL:")
            print(f"  Total: {stats_after['total_pages']} páginas")
            print(f"  Redução: {stats_before['total_pages'] - stats_after['total_pages']} páginas")
        else:
            print("❌ Falha no processamento")
    else:
        print("\n✅ PDF já está otimizado - nenhuma página vazia detectada")


if __name__ == "__main__":
    test_pdf_postprocessor()