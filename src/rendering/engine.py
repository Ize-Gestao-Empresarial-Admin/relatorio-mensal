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
            '--margin-top', '5mm', '--margin-bottom', '4mm',
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

    def render_to_pdf(self, relatorios_data: List[Tuple[str, Any]], cliente_nome: str, 
                  mes_nome: str, ano: int, output_path: str = None) -> str: # type: ignore
        from src.rendering.renderers import get_renderer

        try:
            self._clean_temp_files()
            pdf_paths = []
            processed_reports = []
            relatorios_selecionados = [rel_nome for rel_nome, _ in relatorios_data if rel_nome != "Índice"]

            for index, (rel_nome, dados) in enumerate(relatorios_data):
                if rel_nome == "Índice":
                    renderer = get_renderer(0)
                    if not renderer:
                        logger.warning("Renderizador do índice não encontrado. Ignorando.")
                        continue
                    try:
                        if not isinstance(dados, dict):
                            logger.error(f"Dados inválidos para o índice: esperado dicionário, recebido {type(dados)}: {dados}")
                            raise ValueError(f"Dados inválidos para o índice: esperado dicionário, recebido {type(dados)}")
                        logger.debug(f"Renderizando índice com dados: {dados}")
                        html = renderer.render(dados, cliente_nome, mes_nome, ano)
                        if not isinstance(html, str) or not html.strip():
                            logger.warning("HTML inválido para o índice. Ignorando.")
                            continue
                        pdf_path = self._render_html_to_pdf(html, "Indice")
                        if pdf_path:
                            pdf_paths.insert(0, pdf_path)
                            processed_reports.append("Índice")
                        else:
                            logger.error("Falha ao gerar PDF do índice.")
                    except Exception as e:
                        logger.error(f"Erro ao processar índice: {str(e)}", exc_info=True)
                        continue
                else:
                    try:
                        rel_num = int(rel_nome.split()[1])
                        expected_name = f"Relatório {rel_num}"
                        if rel_nome != expected_name:
                            logger.warning(f"Nome do relatório '{rel_nome}' corrigido para '{expected_name}'.")
                            rel_nome = expected_name
                    except (IndexError, ValueError) as e:
                        logger.warning(f"Ignorando relatório '{rel_nome}' devido a nome inválido: {e}")
                        continue

                    renderer = get_renderer(rel_num)
                    if not renderer:
                        logger.info(f"Renderizador não encontrado para relatório {rel_num}. Ignorando.")
                        continue

                    if not dados or not isinstance(dados, tuple) or len(dados) < 2:
                        logger.warning(f"Dados inválidos para relatório {rel_num}. Ignorando.")
                        continue

                    try:
                        html = renderer.render(dados, cliente_nome, mes_nome, ano)
                        if not isinstance(html, str) or not html.strip():
                            logger.warning(f"HTML inválido para relatório {rel_num}. Tipo: {type(html)}, Conteúdo: {html[:100] if isinstance(html, str) else html}")
                            continue
                        pdf_path = self._render_html_to_pdf(html, rel_nome)
                        if pdf_path:
                            pdf_paths.append(pdf_path)
                            processed_reports.append(rel_nome)
                    except Exception as e:
                        logger.error(f"Erro ao processar relatório {rel_num}: {str(e)}")
                        continue

            if not pdf_paths:
                raise ValueError("Nenhum relatório válido foi renderizado.")

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
            logger.info(f"Relatórios processados: {', '.join(processed_reports)}")
            return output_path

        finally:
            self._clean_temp_files()