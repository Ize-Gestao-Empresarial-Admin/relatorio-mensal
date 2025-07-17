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
import concurrent.futures
from multiprocessing import cpu_count
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
        """Combina múltiplos PDFs em um único arquivo."""
        writer = PdfWriter()

        # Adicionar capa, se existir
        if capa_path and os.path.exists(capa_path):
            capa_reader = PdfUtils.read_pdf(capa_path)
            if capa_reader:
                for page in capa_reader.pages:
                    writer.add_page(page)
                logger.info(f"Capa adicionada: {capa_path}")

        # Adicionar relatórios
        for pdf_path in pdf_paths:
            reader = PdfUtils.read_pdf(pdf_path)
            if reader:
                for page in reader.pages:
                    writer.add_page(page)
                logger.info(f"Relatório adicionado: {pdf_path}")

        # Adicionar páginas de marketing
        if marketing_paths:
            for marketing_path in marketing_paths:
                if os.path.exists(marketing_path):
                    reader = PdfUtils.read_pdf(marketing_path)
                    if reader:
                        for page in reader.pages:
                            writer.add_page(page)
                        logger.info(f"Marketing adicionado: {marketing_path}")
                else:
                    logger.warning(f"Arquivo de marketing não encontrado: {marketing_path}")

        # Salvar PDF combinado
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            writer.write(f)
        logger.info(f"PDF combinado salvo em: {output_path}")

class RenderingEngine:
    """Motor central de renderização que coordena a geração de relatórios em PDF."""
    
    def __init__(self, max_workers: int = None):
        # Configuração do ambiente Jinja2
        templates_dir = os.path.abspath("templates")
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True
        )
        self.temp_files: List[str] = []
        self.temp_files_lock = threading.Lock()
        # Usar metade dos CPUs disponíveis para evitar sobrecarga
        self.max_workers = max_workers or max(1, cpu_count() // 2)

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
        """Converte HTML para PDF e retorna o caminho do PDF temporário."""
        # Gerar identificador único para evitar conflitos
        unique_id = str(uuid.uuid4())
        html_path = tempfile.NamedTemporaryFile(delete=False, suffix=f'_{rel_name}_{unique_id}.html', mode='w', encoding='utf-8').name
        pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=f'_{rel_name}_{unique_id}.pdf').name
        
        self.temp_files.extend([html_path, pdf_path])
        
        # Salvar HTML
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Converter para PDF
        cmd = [
            'wkhtmltopdf', '--enable-local-file-access', '--page-size', 'A4',
            '--margin-top', '5mm', '--margin-bottom', '5mm',
            '--margin-left', '10mm', '--margin-right', '10mm',
            '--no-footer-line', html_path, pdf_path
        ]
        
        try:
            subprocess.run(cmd, check=True)
            logger.info(f"PDF gerado para {rel_name}: {pdf_path}")
            return pdf_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao converter HTML para PDF ({rel_name}): {e}")
            return None # type: ignore
        finally:
            os.unlink(html_path)
            self.temp_files.remove(html_path)

    def _render_html_to_pdf_safe(self, html: str, rel_name: str) -> str:
        """Versão thread-safe e otimizada do _render_html_to_pdf."""
        conversion_start = time.time()
        
        # Gerar identificador único para evitar conflitos
        unique_id = str(uuid.uuid4())
        html_path = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=f'_{rel_name}_{unique_id}.html', 
            mode='w', 
            encoding='utf-8'
        ).name
        pdf_path = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=f'_{rel_name}_{unique_id}.pdf'
        ).name
        
        # Thread-safe addition to temp_files
        with self.temp_files_lock:
            self.temp_files.extend([html_path, pdf_path])
        
        try:
            # Salvar HTML
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            # Converter para PDF com configurações otimizadas
            cmd = [
                'wkhtmltopdf', 
                '--enable-local-file-access', 
                '--page-size', 'A4',
                '--margin-top', '5mm', 
                '--margin-bottom', '5mm',
                '--margin-left', '10mm', 
                '--margin-right', '10mm',
                '--no-footer-line', 
                '--quiet',  # Reduzir output verboso
                '--disable-plugins',  # Desabilitar plugins para acelerar
                '--no-images',  # Se não precisar de imagens externas
                '--load-error-handling', 'ignore',  # Ignorar erros de carregamento
                '--load-media-error-handling', 'ignore',  # Ignorar erros de mídia
                html_path, 
                pdf_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True, timeout=60)  # Timeout de 60s
            conversion_time = time.time() - conversion_start
            logger.info(f"🎯 {rel_name} convertido em {conversion_time:.2f}s")
            return pdf_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao converter HTML para PDF ({rel_name}): {e}")
            return None
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout na conversão PDF ({rel_name})")
            return None
        finally:
            # Remover arquivo HTML imediatamente após conversão
            try:
                os.unlink(html_path)
                with self.temp_files_lock:
                    if html_path in self.temp_files:
                        self.temp_files.remove(html_path)
            except Exception:
                pass

    def _process_single_report(self, args: tuple) -> tuple:
        """Processa um único relatório. Para uso com ThreadPoolExecutor."""
        rel_nome, dados, cliente_nome, mes_nome, ano = args
        
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
            
            if not isinstance(html, str) or not html.strip():
                return None, rel_nome, "HTML inválido"
            
            pdf_path = self._render_html_to_pdf_safe(html, rel_nome)
            
            # Verificar se a conversão foi bem-sucedida
            if pdf_path:
                return pdf_path, rel_nome, "Sucesso"
            else:
                # Capturar e retornar o erro específico da conversão
                error_msg = f"Falha na conversão PDF para {rel_nome}"
                logger.error(error_msg)
                return None, rel_nome, error_msg
            
        except Exception as e:
            error_msg = f"Erro ao processar {rel_nome}: {str(e)}"
            logger.error(error_msg)
            return None, rel_nome, error_msg

    def render_to_pdf(self, relatorios_data: List[Tuple[str, Any]], cliente_nome: str, 
                      mes_nome: str, ano: int, output_path: str = None) -> str:
        """Renderiza relatórios em paralelo para PDF mantendo a ordem correta."""
        try:
            
            start_time = time.time() 
            
            self._clean_temp_files()

            # Definir ordem correta dos relatórios
            ordem_relatorios = [
                "Índice",
                "Relatório 1", "Relatório 2", "Relatório 3", "Relatório 4",
                "Relatório 5", "Relatório 6", "Relatório 7", "Relatório 8"
            ]
            
            # Preparar argumentos para processamento paralelo
            process_args = [
                (rel_nome, dados, cliente_nome, mes_nome, ano) 
                for rel_nome, dados in relatorios_data
            ]
            
            pdf_paths = []
            processed_reports = []
            index_pdf_path = None
            
            # Dicionário para mapear nome do relatório -> resultado
            relatorios_resultados = {}
            
            # Processar relatórios em paralelo
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                logger.info(f"Processando {len(process_args)} relatórios com {self.max_workers} workers...")
                
                # Submeter todas as tarefas
                future_to_rel_nome = {
                    executor.submit(self._process_single_report, args): args[0]
                    for args in process_args
                }
                
                # Coletar resultados conforme completam (sem ordem específica)
                for future in concurrent.futures.as_completed(future_to_rel_nome):
                    rel_nome = future_to_rel_nome[future]
                    
                    try:
                        pdf_path, rel_nome_result, status = future.result()
                        
                        # Armazenar resultado no dicionário
                        relatorios_resultados[rel_nome] = {
                            'pdf_path': pdf_path,
                            'rel_nome_result': rel_nome_result,
                            'status': status
                        }
                        
                        if pdf_path:
                            logger.info(f"✓ {rel_nome_result} processado com sucesso")
                        else:
                            logger.warning(f"✗ {rel_nome_result}: {status}")
                            
                    except Exception as e:
                        logger.error(f"✗ Erro no processamento de {rel_nome}: {str(e)}")
                        relatorios_resultados[rel_nome] = {
                            'pdf_path': None,
                            'rel_nome_result': rel_nome,
                            'status': f"Erro: {str(e)}"
                        }
            
            # Organizar PDFs na ordem correta
            for rel_nome in ordem_relatorios:
                if rel_nome in relatorios_resultados:
                    resultado = relatorios_resultados[rel_nome]
                    pdf_path = resultado['pdf_path']
                    
                    if pdf_path:
                        if rel_nome == "Índice":
                            index_pdf_path = pdf_path
                        else:
                            pdf_paths.append(pdf_path)
                        processed_reports.append(resultado['rel_nome_result'])
            
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
            
            processing_time = time.time() - start_time
            logger.info(f"✓ Processamento concluído em {processing_time:.2f}s")
            logger.info(f"Performance: {len(processed_reports)/processing_time:.1f} relatórios/segundo")
            
            return output_path
            
        finally:
            self._clean_temp_files()