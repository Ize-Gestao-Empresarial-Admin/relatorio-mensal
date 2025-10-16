from jinja2 import Environment, FileSystemLoader
import os
import tempfile
import subprocess
from pathlib import Path
from typing import List, Tuple, Any
from pypdf import PdfReader, PdfWriter
import io
import logging
import re
import glob
import time
import shutil
import uuid
from datetime import datetime
import threading

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PdfUtils:
    """Utilitários para manipulação de arquivos PDF."""
    
    @staticmethod
    def read_pdf(pdf_path: str) -> PdfReader:
        """Lê um arquivo PDF e retorna um PdfReader."""
        try:
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            reader = PdfReader(io.BytesIO(pdf_bytes))
            if len(reader.pages) == 0:
                logger.warning(f"PDF {pdf_path} está vazio.")
                return None # type: ignore
            return reader
        except Exception as e:
            logger.error(f"Erro ao ler PDF {pdf_path}: {e}")
            return None # type: ignore

    @staticmethod
    def combine_pdfs(pdf_paths: List[str], output_path: str, capa_path: str = None, marketing_paths: List[str] = None) -> None: # type: ignore
        """Combina múltiplos PDFs em um único arquivo, detectando e removendo páginas vazias."""
        writer = PdfWriter()
        total_pages_added = 0

        # Adicionar capa, se existir
        if capa_path and os.path.exists(capa_path):
            capa_reader = PdfUtils.read_pdf(capa_path)
            if capa_reader:
                for page in capa_reader.pages:
                    writer.add_page(page)
                    total_pages_added += 1
                logger.info(f"Capa adicionada: {capa_path} ({len(capa_reader.pages)} páginas)")

        # Adicionar relatórios com detecção de páginas vazias
        for pdf_path in pdf_paths:
            if not os.path.exists(pdf_path):
                logger.warning(f"Arquivo PDF não encontrado: {pdf_path}")
                continue
                
            # Verificar se o arquivo não está vazio
            if os.path.getsize(pdf_path) == 0:
                logger.warning(f"Arquivo PDF vazio ignorado: {pdf_path}")
                continue
                
            reader = PdfUtils.read_pdf(pdf_path)
            if reader:
                pages_added = 0
                for page_num, page in enumerate(reader.pages, 1):
                    # Verificação mais robusta do conteúdo da página
                    try:
                        text = page.extract_text().strip()
                        has_text = len(text) > 0
                        
                        # Verificar se tem recursos visuais (imagens, gráficos, etc)
                        has_resources = False
                        try:
                            resources = page.get('/Resources', {})
                            has_resources = (
                                '/XObject' in resources or 
                                '/Font' in resources or 
                                '/ExtGState' in resources or
                                len(str(resources)) > 50  # Indicador de conteúdo significativo
                            )
                        except:
                            pass
                        
                        # Heurística: se o PDF tem tamanho razoável, provavelmente tem conteúdo
                        pdf_size = os.path.getsize(pdf_path)
                        likely_has_content = pdf_size > 10000  # 10KB
                        
                        # Decidir se adicionar a página
                        should_add = has_text or has_resources or likely_has_content
                        
                        if should_add:
                            writer.add_page(page)
                            pages_added += 1
                            total_pages_added += 1
                            
                            if has_text:
                                logger.debug(f"✅ Página {page_num} adicionada (com texto): {pdf_path}")
                            elif has_resources:
                                logger.info(f"📄 Página {page_num} adicionada (sem texto, mas com recursos): {pdf_path}")
                            else:
                                logger.info(f"📄 Página {page_num} adicionada (heurística - PDF grande): {pdf_path}")
                        else:
                            logger.warning(f"❌ Página {page_num} VAZIA ignorada em: {pdf_path}")
                            
                    except Exception as e:
                        # Se houver erro na verificação, adicionar a página por segurança
                        logger.warning(f"⚠️ Erro ao verificar página {page_num}, adicionando por segurança: {e}")
                        writer.add_page(page)
                        pages_added += 1
                        total_pages_added += 1
                        
                logger.info(f"📑 Relatório adicionado: {os.path.basename(pdf_path)} ({pages_added} páginas válidas)")
            else:
                logger.error(f"❌ Falha ao ler PDF: {pdf_path}")

        # Adicionar páginas de marketing
        if marketing_paths:
            for marketing_path in marketing_paths:
                if os.path.exists(marketing_path):
                    reader = PdfUtils.read_pdf(marketing_path)
                    if reader:
                        for page in reader.pages:
                            writer.add_page(page)
                            total_pages_added += 1
                        logger.info(f"Marketing adicionado: {marketing_path} ({len(reader.pages)} páginas)")
                else:
                    logger.warning(f"Arquivo de marketing não encontrado: {marketing_path}")

        # Verificar se temos páginas para salvar
        if total_pages_added == 0:
            raise ValueError("Nenhuma página válida foi encontrada para combinar no PDF")

        # Salvar PDF combinado
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            writer.write(f)
        logger.info(f"PDF combinado salvo em: {output_path} (total: {total_pages_added} páginas válidas)")

class RenderingEngine:
    """Motor central de renderização que coordena a geração de relatórios em PDF."""
    
    def __init__(self):
        # Configuração do ambiente Jinja2
        templates_dir = os.path.abspath("templates")
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True
        )
        self.temp_files: List[str] = []

    def _clean_temp_files(self) -> None:
        """Remove arquivos temporários gerados durante a renderização."""
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
                logger.debug(f"Removido arquivo temporário: {temp_file}")
            except Exception as e:
                logger.warning(f"Erro ao remover arquivo temporário {temp_file}: {e}")
        self.temp_files.clear()

    def _render_html_to_pdf(self, html: str, rel_name: str) -> str:
        """Converte HTML para PDF (usando footer nativo do wkhtmltopdf) e retorna o caminho do PDF temporário."""
        # Gerar identificadores e arquivos temporários
        unique_id = str(uuid.uuid4())
        html_path = tempfile.NamedTemporaryFile(delete=False, suffix=f'_{rel_name}_{unique_id}.html', mode='w', encoding='utf-8').name
        pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=f'_{rel_name}_{unique_id}.pdf').name
        footer_path = tempfile.NamedTemporaryFile(delete=False, suffix=f'_{rel_name}_{unique_id}_footer.html', mode='w', encoding='utf-8').name

        self.temp_files.extend([html_path, pdf_path, footer_path])

        # Salvar HTML do relatório
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

        # Caminho do executável wkhtmltopdf (permite sobrepor via .env)
        wkhtmltopdf_cmd = os.getenv("WKHTMLTOPDF_CMD", "wkhtmltopdf")

        # Caminho do PNG do rodapé (permite sobrepor via .env, senão usa assets/icons/rodape.png)
        rodape_img = os.getenv("RODAPE_IMG_PATH", os.path.abspath("assets/icons/rodape.png"))
        rodape_url = "file:///" + rodape_img.replace("\\", "/")

        # HTML simples do footer (centrado, altura controlada em mm)
        footer_html = f"""<!doctype html>
        <html><head><meta charset="utf-8">
        <style>
        html,body{{margin:0;padding:0}}
        .wrap{{width:100%;text-align:center}}
        img{{height:12mm;width:auto}}
        </style></head>
        <body>
        <div class="wrap"><img src="{rodape_url}" alt="rodapé"/></div>
        </body></html>"""

        with open(footer_path, 'w', encoding='utf-8') as f:
            f.write(footer_html)

        # Comando wkhtmltopdf com fallback para produção
        # Em produção, o Qt pode não suportar alguns switches
        base_cmd = [
            wkhtmltopdf_cmd,
            '--enable-local-file-access',
            '--page-size', 'A4',
            '--margin-top', '10mm',
            '--margin-bottom', '18mm',
            '--margin-left', '6mm',
            '--margin-right', '6mm',
        ]
        
        # Detectar se estamos em produção (Streamlit Cloud)
        is_production = os.getenv('STREAMLIT_SHARING_MODE') or '/mount/src/' in os.getcwd()
        
        if is_production:
            # Em produção, não usar switches de footer que podem não funcionar
            logger.info("🌐 Modo produção detectado - usando configuração simplificada do wkhtmltopdf")
            cmd = base_cmd + [html_path, pdf_path]
        else:
            # Localmente, usar configuração completa com footer
            cmd = base_cmd + [
                '--no-footer-line',
                '--footer-html', footer_path,
                '--footer-spacing', '0',
                html_path, pdf_path
            ]

        keep = os.getenv("KEEP_WKHTML_HTML") == "1"
        try:
            # DEBUG: Log detalhado do comando e conteúdo HTML
            logger.info(f"🔧 Executando wkhtmltopdf para {rel_name}")
            logger.debug(f"📄 HTML size: {len(html)} caracteres")
            logger.debug(f"📄 HTML snippet: {html[:200]}...")
            logger.debug(f"🖥️ Comando: {' '.join(cmd)}")
            
            subprocess.run(cmd, check=True)
            
            # Verificar se o PDF foi criado corretamente
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                logger.info(f"✅ PDF gerado para {rel_name}: {pdf_path} ({file_size} bytes)")
                
                # Debug adicional: verificar se PDF não está vazio
                if file_size < 1000:
                    logger.warning(f"⚠️ PDF muito pequeno para {rel_name}: {file_size} bytes - possível problema")
                    
            else:
                logger.error(f"❌ PDF não foi criado para {rel_name}")
                return None
                
            return pdf_path
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao converter HTML para PDF ({rel_name}): {e}")
            logger.error(f"🖥️ Comando que falhou: {' '.join(cmd)}")
            logger.error(f"📄 HTML que causou erro (primeiros 500 chars): {html[:500]}...")
            return None
        finally:
            if not keep:
                try: os.unlink(html_path)
                except: pass
                try: os.unlink(footer_path)
                except: pass
                for p in [html_path, footer_path]:
                    if p in self.temp_files:
                        self.temp_files.remove(p)

    def _process_single_report(self, rel_nome: str, dados: Any, cliente_nome: str, mes_nome: str, ano: int) -> tuple:
        """Processa um único relatório sequencialmente."""
        conversion_start = time.time()
        
        try:
            if rel_nome == "Índice":
                from src.rendering.renderers import get_renderer
                renderer = get_renderer(0)
                if not renderer or not isinstance(dados, dict):
                    return None, rel_nome, "Dados inválidos para índice"
                
                html = renderer.render(dados, cliente_nome, mes_nome, ano)
                
            else:
                # Extrair número do relatório
                try:
                    rel_num = int(rel_nome.split()[1])
                except (IndexError, ValueError):
                    return None, rel_nome, "Nome de relatório inválido"
                
                from src.rendering.renderers import get_renderer
                renderer = get_renderer(rel_num)
                if not renderer:
                    return None, rel_nome, "Renderizador não encontrado"
                
                if not dados or not isinstance(dados, tuple) or len(dados) < 2:
                    return None, rel_nome, "Dados inválidos"
                
                html = renderer.render(dados, cliente_nome, mes_nome, ano)
            
            # DEBUG: Verificar conteúdo HTML gerado
            if not isinstance(html, str):
                logger.error(f"❌ {rel_nome}: HTML não é string, tipo: {type(html)}")
                return None, rel_nome, "HTML inválido - tipo incorreto"
                
            html_clean = html.strip()
            if not html_clean:
                logger.error(f"❌ {rel_nome}: HTML está vazio")
                return None, rel_nome, "HTML vazio"
                
            logger.info(f"✅ {rel_nome}: HTML gerado com {len(html_clean)} caracteres")
            
            # Verificar se HTML contém conteúdo mínimo esperado
            if len(html_clean) < 100:
                logger.warning(f"⚠️ {rel_nome}: HTML muito pequeno ({len(html_clean)} chars)")
                logger.debug(f"📄 HTML: {html_clean}")
            elif not any(tag in html_clean.lower() for tag in ['<body>', '<div>', '<table>', '<p>']):
                logger.warning(f"⚠️ {rel_nome}: HTML não contém tags esperadas")
                logger.debug(f"📄 HTML snippet: {html_clean[:200]}...")
            
            pdf_path = self._render_html_to_pdf(html, rel_nome)
            
            conversion_time = time.time() - conversion_start
            
            # Verificar se a conversão foi bem-sucedida
            if pdf_path:
                logger.info(f"🎯 {rel_nome} convertido em {conversion_time:.2f}s")
                return pdf_path, rel_nome, "Sucesso"
            else:
                error_msg = f"Falha na conversão PDF para {rel_nome}"
                logger.error(error_msg)
                return None, rel_nome, error_msg
            
        except Exception as e:
            error_msg = f"Erro ao processar {rel_nome}: {str(e)}"
            logger.error(error_msg)
            return None, rel_nome, error_msg

    def render_to_pdf(self, relatorios_data: List[Tuple[str, Any]], cliente_nome: str, 
                      mes_nome: str, ano: int, output_path: str = None) -> str:
        """Renderiza relatórios sequencialmente para PDF mantendo a ordem correta."""
        try:
            
            start_time = time.time() 
            
            self._clean_temp_files()

            # Definir ordem correta dos relatórios
            ordem_relatorios = [
                "Índice",
                "Relatório 1", "Relatório 2", "Relatório 3", "Relatório 4",
                "Relatório 5", "Relatório 6", "Relatório 7", "Relatório 8"
            ]
            
            pdf_paths = []
            processed_reports = []
            index_pdf_path = None
            
            logger.info(f"Processando {len(relatorios_data)} relatórios sequencialmente...")
            
            # Processar relatórios sequencialmente na ordem correta
            for rel_nome in ordem_relatorios:
                # Encontrar os dados correspondentes ao relatório atual
                dados_relatorio = None
                for rel_nome_data, dados in relatorios_data:
                    if rel_nome_data == rel_nome:
                        dados_relatorio = dados
                        break
                
                if dados_relatorio is None:
                    logger.warning(f"Dados não encontrados para: {rel_nome}")
                    continue
                
                # Processar o relatório
                pdf_path, rel_nome_result, status = self._process_single_report(
                    rel_nome, dados_relatorio, cliente_nome, mes_nome, ano
                )
                
                if pdf_path:
                    if rel_nome == "Índice":
                        index_pdf_path = pdf_path
                    else:
                        pdf_paths.append(pdf_path)
                    processed_reports.append(rel_nome_result)
                    logger.info(f"✓ {rel_nome_result} processado com sucesso")
                else:
                    logger.warning(f"✗ {rel_nome_result}: {status}")
            
            # Adicionar índice no início se existir
            if index_pdf_path:
                pdf_paths.insert(0, index_pdf_path)
            
            if not pdf_paths:
                raise ValueError("Nenhum relatório válido foi renderizado.")
            
            # Combinar PDFs na ordem correta: capa, índice, relatórios, marketing
            capa_path = os.path.abspath("assets/images/capa.pdf")
            marketing_paths = [
                os.path.abspath("assets/images/pdf_marketing_1.pdf"),
                os.path.abspath("assets/images/pdf_marketing_2.pdf")
            ]
            
            if not output_path:
                output_path = os.path.join(
                    "outputs", 
                    f"Relatorio_{cliente_nome.replace(' ', '_')}_{mes_nome}_{ano}.pdf"
                )
            
            PdfUtils.combine_pdfs(pdf_paths, output_path, capa_path, marketing_paths)
            logger.info(f"✓ PDF final gerado: {output_path}")
            logger.info(f"Relatórios processados na ordem correta: {', '.join(processed_reports)}")
            
            # Aplicar pós-processamento com comparação de template
            # TEMPORARIAMENTE DESABILITADO para diagnóstico em produção
            is_production = os.getenv('STREAMLIT_SHARING_MODE') or '/mount/src/' in os.getcwd()
            enable_postprocessing = not is_production and os.getenv('DISABLE_PDF_POSTPROCESSING', 'false').lower() != 'true'
            
            if enable_postprocessing:
                try:
                    from src.core.pdf_finalizer import PDFinalizer
                    finalizer = PDFinalizer()
                    
                    success, final_path, removed_pages = finalizer.finalize_pdf(output_path)
                    if success and removed_pages:
                        logger.info(f"🧹 Pós-processamento: {len(removed_pages)} páginas vazias removidas")
                        logger.info(f"📋 Páginas removidas: {removed_pages}")
                    else:
                        logger.info("✅ PDF já otimizado, nenhuma página removida")
                except Exception as e:
                    logger.warning(f"⚠️  Falha no pós-processamento (PDF mantido): {e}")
            else:
                if is_production:
                    logger.info("🌐 Pós-processamento desabilitado em produção para diagnóstico")
                else:
                    logger.info("📄 Pós-processamento desabilitado via variável de ambiente")
            
            processing_time = time.time() - start_time
            logger.info(f"✓ Processamento concluído em {processing_time:.2f}s")
            logger.info(f"Performance: {len(processed_reports)/processing_time:.1f} relatórios/segundo")
            
            return output_path
            
        finally:
            self._clean_temp_files()