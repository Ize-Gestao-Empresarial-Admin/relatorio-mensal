#!/usr/bin/env python3
"""
Utilitário para pós-processamento de PDFs - Remove páginas baseado em comparação com template.
VERSÃO: v3.0-template-comparison
"""

import PyPDF2
import logging
import os
import hashlib
from typing import List, Tuple

logger = logging.getLogger(__name__)

class PDFPostProcessor:
    """Classe para pós-processamento de PDFs com comparação de templates."""
    
    # Caminho para o template de página de erro
    ERROR_PAGE_TEMPLATE = "src/example_error_page.pdf"
    
    def __init__(self):
        """Inicializa o post-processor e carrega o template."""
        self.error_page_template = self._load_error_page_template()
    
    def _load_error_page_template(self) -> dict:
        """
        Carrega o template de página de erro e extrai suas características.
        
        Returns:
            Dict com características da página de erro
        """
        template_path = PDFPostProcessor.ERROR_PAGE_TEMPLATE
        
        # Tentar diferentes localizações do template
        possible_paths = [
            template_path,
            os.path.join("src", "example_error_page.pdf"),
            "example_error_page.pdf",
            os.path.join(os.path.dirname(__file__), "example_error_page.pdf")
        ]
        
        # DEBUG: Log detalhado para produção
        logger.info(f"🔍 DEBUG: Procurando template em {len(possible_paths)} localizações:")
        for i, path in enumerate(possible_paths):
            exists = os.path.exists(path)
            abs_path = os.path.abspath(path) if exists else "N/A"
            logger.info(f"  {i+1}. {path} -> EXISTS: {exists} -> ABS: {abs_path}")
        
        for path in possible_paths:
            if os.path.exists(path):
                template_path = path
                logger.info(f"✅ Template encontrado: {template_path}")
                break
        else:
            logger.error(f"❌ Template de página de erro não encontrado em: {possible_paths}")
            logger.error(f"📁 Diretório atual: {os.getcwd()}")
            logger.error(f"📁 __file__ dir: {os.path.dirname(__file__)}")
            return None
        
        try:
            with open(template_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                if len(reader.pages) == 0:
                    logger.error("❌ Template vazio")
                    return None
                
                template_page = reader.pages[0]
                
                # Extrair características da página template
                template_data = {
                    'text': template_page.extract_text().strip(),
                    'text_hash': hashlib.md5(template_page.extract_text().encode()).hexdigest(),
                    'resources': template_page.get('/Resources', {}),
                }
                
                # Extrair hash do conteúdo visual se possível
                try:
                    if '/Contents' in template_page:
                        contents = template_page['/Contents']
                        if hasattr(contents, 'get_data'):
                            content_data = contents.get_data()
                            template_data['content_hash'] = hashlib.md5(content_data).hexdigest()
                except:
                    pass
                
                logger.info(f"✅ Template carregado: {template_path}")
                logger.info(f"📝 Texto template: '{template_data['text'][:50]}...'")
                
                return template_data
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar template: {e}")
            return None
    
    def _is_page_identical_to_template(self, page, template_data: dict = None) -> bool:
        """
        Verifica se uma página é idêntica ao template de erro.
        
        Args:
            page: Página do PDF a ser comparada
            template_data: Dados do template de comparação
            
        Returns:
            True se a página é idêntica ao template
        """
        # Usar template da instância se não fornecido
        if template_data is None:
            template_data = self.error_page_template
            
        if template_data is None:
            logger.warning("⚠️ Template não disponível para comparação")
            return False
            
        try:
            # 1. Comparar texto extraído
            page_text = page.extract_text().strip()
            page_text_hash = hashlib.md5(page_text.encode()).hexdigest()
            
            # DEBUG: Log detalhado da comparação
            template_hash = template_data['text_hash']
            template_text = template_data.get('text', '')
            
            logger.debug(f"🔍 COMPARAÇÃO DEBUG:")
            logger.debug(f"  Página texto (len={len(page_text)}): {repr(page_text[:100])}...")
            logger.debug(f"  Página hash: {page_text_hash}")
            logger.debug(f"  Template texto (len={len(template_text)}): {repr(template_text[:100])}...")
            logger.debug(f"  Template hash: {template_hash}")
            logger.debug(f"  Hash match: {page_text_hash == template_hash}")
            
            # NOVA LÓGICA: Detectar apenas páginas completamente vazias (0 caracteres)
            # NÃO remover páginas baseado no template em produção
            if len(page_text) == 0:
                logger.info("🗑️ Página completamente vazia detectada (0 caracteres)")
                logger.warning(f"⚠️ PRODUÇÃO DEBUG: Página vazia removida - 0 caracteres")
                return True
            
            # DESABILITADO TEMPORARIAMENTE: Comparação com template
            # Esta lógica estava removendo páginas válidas em produção
            if False and page_text_hash == template_data['text_hash']:
                logger.info("🎯 Página idêntica detectada por hash de texto")
                logger.warning(f"⚠️ PRODUÇÃO DEBUG: Página removida - texto='{page_text[:50]}' hash={page_text_hash}")
                return True
            
            # DESABILITADO: Comparar conteúdo visual se disponível
            if False and 'content_hash' in template_data:
                try:
                    if '/Contents' in page:
                        contents = page['/Contents']
                        if hasattr(contents, 'get_data'):
                            page_content_data = contents.get_data()
                            page_content_hash = hashlib.md5(page_content_data).hexdigest()
                            
                            if page_content_hash == template_data['content_hash']:
                                logger.info("🎯 Página idêntica detectada por hash de conteúdo")
                                logger.warning(f"⚠️ PRODUÇÃO DEBUG: Página removida por conteúdo - hash={page_content_hash}")
                                return True
                except:
                    pass
            
            # DESABILITADO: Comparação texto exato como fallback
            if False and page_text == template_text and len(page_text) > 0:
                logger.info("🎯 Página idêntica detectada por texto exato")
                logger.warning(f"⚠️ PRODUÇÃO DEBUG: Página removida por texto exato - '{page_text[:50]}'")
                return True
                
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao comparar página: {e}")
            return False
    
    def _is_page_empty_advanced(self, page_text: str) -> bool:
        """
        Verifica se uma página está vazia usando lógica avançada.
        
        Args:
            page_text: Texto extraído da página
            
        Returns:
            True se a página deve ser considerada vazia
        """
        # 1. Página completamente vazia
        if len(page_text) == 0:
            logger.info("🗑️ Página completamente vazia detectada (0 caracteres)")
            return True
        
        # 2. Apenas espaços em branco
        if len(page_text.strip()) == 0:
            logger.info("🗑️ Página com apenas espaços detectada")
            return True
        
        # 3. Comparar com template se disponível
        if self.error_page_template:
            page_text_hash = hashlib.md5(page_text.encode()).hexdigest()
            if page_text_hash == self.error_page_template['text_hash']:
                logger.info("🎯 Página idêntica ao template detectada")
                return True
            
            # 4. Comparação de texto exato
            template_text = self.error_page_template['text']
            if page_text == template_text and len(page_text) > 0:
                logger.info("🎯 Página idêntica detectada por texto exato")
                return True
        
        return False
    
    def remove_blank_pages(self, pdf_path: str, output_path: str = None) -> Tuple[bool, str, List[int]]:
        """
        Remove páginas idênticas ao template de erro de um PDF.
        NOVA ABORDAGEM: Comparação exata com template example_error_page.pdf
        
        Args:
            pdf_path: Caminho do PDF original
            output_path: Caminho do PDF de saída (se None, sobrescreve o original)
            
        Returns:
            Tupla (sucesso, caminho_final, paginas_removidas)
        """
        if output_path is None:
            output_path = pdf_path
            
        # Carregar template de página de erro
        template_data = self.error_page_template
        if template_data is None:
            logger.warning("⚠️ Template não carregado - mantendo todas as páginas")
            return True, pdf_path, []
        
        blank_pages = []
        total_pages = 0
        
        try:
            with open(pdf_path, 'rb') as input_file:
                reader = PyPDF2.PdfReader(input_file)
                writer = PyPDF2.PdfWriter()
                total_pages = len(reader.pages)
                
                logger.info(f"📄 Analisando PDF: {pdf_path} ({total_pages} páginas)")
                logger.info("🔍 NOVO ALGORITMO: Comparação com template de erro")
                
                for page_num, page in enumerate(reader.pages, 1):
                    try:
                        # Verificar se página é idêntica ao template
                        is_error_page = self._is_page_identical_to_template(page, template_data)
                        
                        if not is_error_page:
                            # Página diferente do template - manter
                            writer.add_page(page)
                            logger.debug(f"✅ Página {page_num}: MANTIDA (diferente do template)")
                        else:
                            # Página idêntica ao template de erro - remover
                            blank_pages.append(page_num)
                            logger.warning(f"❌ Página {page_num}: REMOVIDA (idêntica ao template de erro)")
                                
                    except Exception as e:
                        # Em caso de erro, manter a página por segurança
                        writer.add_page(page)
                        logger.warning(f"⚠️ Página {page_num}: Erro ao analisar, mantida: {e}")
                
                # Salvar apenas se há páginas para salvar
                if len(writer.pages) > 0:
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    pages_kept = len(writer.pages)
                    pages_removed = len(blank_pages)
                    
                    logger.info(f"🎯 PDF processado: {pages_kept} páginas mantidas, {pages_removed} removidas")
                    
                    if blank_pages:
                        logger.info(f"📋 Páginas removidas: {blank_pages}")
                    
                    return True, output_path, blank_pages
                else:
                    logger.error(f"❌ Erro: PDF ficaria vazio após remoção")
                    return False, pdf_path, blank_pages
                    
        except Exception as e:
            logger.error(f"❌ Erro ao processar PDF {pdf_path}: {e}")
            return False, pdf_path, []
    
    def analyze_pdf_content(self, pdf_path: str) -> dict:
        """
        Analisa o conteúdo de um PDF usando comparação com template.
        
        Args:
            pdf_path: Caminho do PDF
            
        Returns:
            Dicionário com estatísticas do PDF
        """
        stats = {
            'total_pages': 0,
            'error_pages': [],  # Páginas idênticas ao template
            'good_pages': [],   # Páginas com conteúdo real
            'analysis_errors': []
        }
        
        # Carregar template
        template_data = self.error_page_template
        if template_data is None:
            logger.warning("⚠️ Análise sem template - todas as páginas consideradas válidas")
            
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                stats['total_pages'] = len(reader.pages)
                
                for page_num, page in enumerate(reader.pages, 1):
                    try:
                        if template_data and self._is_page_identical_to_template(page, template_data):
                            stats['error_pages'].append(page_num)
                        else:
                            stats['good_pages'].append(page_num)
                            
                    except Exception as e:
                        stats['analysis_errors'].append(page_num)
                        logger.warning(f"Erro ao analisar página {page_num}: {e}")
                        
        except Exception as e:
            logger.error(f"Erro ao analisar PDF {pdf_path}: {e}")
            
        return stats


def test_pdf_postprocessor():
    """Função de teste para o novo pós-processador baseado em template."""
    import glob
    
    print("🧪 TESTE DO PÓS-PROCESSADOR v3.0 - COMPARAÇÃO COM TEMPLATE")
    print("=" * 60)
    
    # Verificar se template existe
    template_path = "src/example_error_page.pdf"
    if not os.path.exists(template_path):
        print(f"❌ Template não encontrado: {template_path}")
        return
    
    print(f"✅ Template encontrado: {template_path}")
    
    # Buscar PDFs na pasta outputs
    pdf_files = glob.glob("outputs/*.pdf")
    
    if not pdf_files:
        print("❌ Nenhum PDF encontrado na pasta outputs/")
        return
    
    # Usar o PDF mais recente
    pdf_path = max(pdf_files, key=os.path.getctime)
    print(f"📁 Testando com: {os.path.basename(pdf_path)}")
    
    # Criar instância do post-processor
    postprocessor = PDFPostProcessor()
    
    # Analisar antes
    stats_before = postprocessor.analyze_pdf_content(pdf_path)
    print(f"\n📊 ANÁLISE INICIAL:")
    print(f"  Total: {stats_before['total_pages']} páginas")
    print(f"  ❌ Páginas de erro: {stats_before['error_pages']}")
    print(f"  ✅ Páginas válidas: {stats_before['good_pages']}")
    print(f"  ⚠️ Erros de análise: {stats_before['analysis_errors']}")
    
    if stats_before['error_pages']:
        print(f"\n🔧 Processando remoção de {len(stats_before['error_pages'])} páginas de erro...")
        
        # Fazer cópia para teste
        output_path = pdf_path.replace('.pdf', '_PROCESSADO.pdf')
        success, final_path, removed_pages = postprocessor.remove_blank_pages(pdf_path, output_path)
        
        if success:
            print(f"✅ PDF processado: {os.path.basename(final_path)}")
            print(f"📋 Páginas removidas: {removed_pages}")
            
            # Analisar depois
            stats_after = postprocessor.analyze_pdf_content(final_path)
            print(f"\n📊 ANÁLISE FINAL:")
            print(f"  Total: {stats_after['total_pages']} páginas")
            print(f"  Redução: {stats_before['total_pages'] - stats_after['total_pages']} páginas")
        else:
            print("❌ Falha no processamento")
    else:
        print("\n✅ PDF já está otimizado - nenhuma página de erro detectada")


if __name__ == "__main__":
    test_pdf_postprocessor()