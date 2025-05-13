# src/rendering/engine.py
from jinja2 import Environment, FileSystemLoader
import os
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple
from PyPDF2 import PdfReader, PdfWriter
import io

class RenderingEngine:
    """Motor central de renderização que coordena a geração de relatórios em PDF."""
    
    def __init__(self):
        # Configuração do ambiente Jinja2
        templates_dir = os.path.abspath("templates")
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True
        )
    
    def render_to_pdf(self, relatorios_data: List[Tuple[str, Any]], cliente_nome: str, 
                      mes_nome: str, ano: int, output_path: str = None) -> str:
        """
        Renderiza múltiplos relatórios em um único PDF, com capa e anexos de marketing no final.
        
        Args:
            relatorios_data: Lista de tuplas (nome_relatorio, dados)
            cliente_nome: Nome do cliente
            mes_nome: Nome do mês
            ano: Ano do relatório
            output_path: Caminho para salvar o PDF (opcional)
            
        Returns:
            Caminho do arquivo PDF gerado
        """
        from src.rendering.renderers import get_renderer
        
        html_parts = []
        
        # Renderiza cada relatório
        for rel_nome, dados in relatorios_data:
            # Extrai o número do relatório do nome (ex: "Relatório 7 - ..." -> 7)
            rel_num = int(rel_nome.split()[1])
            
            # Obtém o renderizador apropriado
            renderer = get_renderer(rel_num)
            if renderer:
                html = renderer.render(dados, cliente_nome, mes_nome, ano)
                html_parts.append(html)
            else:
                raise ValueError(f"Renderizador não encontrado para o relatório {rel_num} ({rel_nome})")
        
        # Combina todos os HTMLs
        if not html_parts:
            raise ValueError("Nenhum relatório foi renderizado. Verifique os dados ou os renderizadores.")
        full_html = "\n".join(html_parts)
        
        # Define caminho de saída se não fornecido
        if not output_path:
            output_path = os.path.join("outputs", f"Relatorio_{cliente_nome.replace(' ', '_')}_{mes_nome}_{ano}.pdf")
        
        # Cria diretório de saída se não existir
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Salva HTML temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as f:
            html_path = f.name
            f.write(full_html)
        
        # Define caminho temporário para o PDF inicial
        temp_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf').name
        
        # Converte HTML para PDF usando wkhtmltopdf
        try:
            cmd = ['wkhtmltopdf', '--enable-local-file-access', '--page-size', 'A4', 
                   '--margin-top', '5mm', '--margin-bottom', '10mm', 
                   '--margin-left', '10mm', '--margin-right', '10mm',
                   html_path, temp_pdf_path]
            
            subprocess.run(cmd, check=True)
            
            # Remove arquivo HTML temporário
            os.unlink(html_path)
            
            # Adicionar capa ao PDF
            capa_path = os.path.abspath("assets/images/capa.pdf")
            marketing_paths = [
                os.path.abspath("assets/images/pdf_marketing_1.pdf"),
                os.path.abspath("assets/images/pdf_marketing_2.pdf")
            ]
            
            # Ler relatório inicial
            with open(temp_pdf_path, "rb") as f:
                pdf_bytes = f.read()
            relatorio_reader = PdfReader(io.BytesIO(pdf_bytes))
            
            # Criar escritor para o PDF final
            writer = PdfWriter()
            
            # Adicionar capa, se existir
            if os.path.exists(capa_path):
                with open(capa_path, "rb") as f:
                    capa_bytes = f.read()
                capa_reader = PdfReader(io.BytesIO(capa_bytes))
                for page in capa_reader.pages:
                    writer.add_page(page)
            
            # Adicionar páginas do relatório
            for page in relatorio_reader.pages:
                writer.add_page(page)
            
            # Adicionar os arquivos de marketing, se existirem
            for marketing_path in marketing_paths:
                if os.path.exists(marketing_path):
                    with open(marketing_path, "rb") as f:
                        marketing_bytes = f.read()
                    marketing_reader = PdfReader(io.BytesIO(marketing_bytes))
                    for page in marketing_reader.pages:
                        writer.add_page(page)
            
            # Salvar PDF resultante
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            # Remove arquivo PDF temporário
            os.unlink(temp_pdf_path)
            
            return output_path
                
        except Exception as e:
            # Remove arquivos temporários em caso de erro
            if os.path.exists(html_path):
                os.unlink(html_path)
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
            raise Exception(f"Erro ao gerar PDF: {str(e)}")