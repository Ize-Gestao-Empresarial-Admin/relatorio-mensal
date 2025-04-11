# src/interfaces/pdf_generator.py
import os
from jinja2 import Environment, FileSystemLoader
import pdfkit
from src.interfaces.graficos import Graficos
import logging

logger = logging.getLogger(__name__)

class PDFGenerator:
    def __init__(self, template_dir="templates", static_dir="static"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.static_dir = static_dir
        self.graficos = Graficos(static_dir=os.path.join(static_dir, "graficos"))
        self.wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
        self.config = pdfkit.configuration(wkhtmltopdf=self.wkhtmltopdf_path)

    def _caminho_para_url(self, caminho):
        """Converte um caminho de arquivo para URL de formato file://"""
        caminho_abs = os.path.abspath(caminho)
        url = f"file:///{caminho_abs.replace(os.sep, '/')}"
        if os.path.exists(caminho_abs):
            logger.info(f"Caminho convertido para URL: {url}")
            return url
        logger.warning(f"Arquivo não encontrado: {caminho_abs}")
        return ""

    def generate_pdf(self, relatorios_dados, empresa, mes, ano, output_path):
        html_content = ""
        
        for rel_nome, dados in relatorios_dados:
            if rel_nome == "Relatório 1 - Resultados Mensais":
                path_grafico = self.graficos.grafico_r1(dados, empresa, mes, ano)
                url_grafico = self._caminho_para_url(path_grafico)
                context = {"titulo": rel_nome, "empresa": empresa, "mes": mes, "ano": ano, "dados": dados, "grafico": url_grafico}
                template = self.env.get_template("relatorio_1.html")
                html_content += template.render(context)
            
            elif rel_nome == "Relatório 2 - Análise por Competência":
                path_grafico = self.graficos.grafico_r2(dados, empresa, mes, ano)
                url_grafico = self._caminho_para_url(path_grafico)
                context = {"titulo": rel_nome, "empresa": empresa, "mes": mes, "ano": ano, "dados": dados, "grafico": url_grafico}
                template = self.env.get_template("relatorio_2.html")
                html_content += template.render(context)
            
            elif rel_nome == "Relatório 3 - Análise de Lucros":
                path_grafico = self.graficos.grafico_r3(dados, empresa, mes, ano)
                url_grafico = self._caminho_para_url(path_grafico)
                context = {"titulo": rel_nome, "empresa": empresa, "mes": mes, "ano": ano, "dados": dados, "grafico": url_grafico}
                template = self.env.get_template("relatorio_3.html")
                html_content += template.render(context)
            
            elif rel_nome == "Relatório 4 - Evolução":
                path_grafico = self.graficos.grafico_r4(dados, empresa, mes, ano)
                url_grafico = self._caminho_para_url(path_grafico)
                context = {"titulo": rel_nome, "empresa": empresa, "mes": mes, "ano": ano, "dados": dados, "grafico": url_grafico}
                template = self.env.get_template("relatorio_4.html")
                html_content += template.render(context)
            
            elif rel_nome == "Relatório 5 - Indicadores":
                context = {"titulo": rel_nome, "empresa": empresa, "mes": mes, "ano": ano, "dados": dados["Indicadores"]}
                template = self.env.get_template("relatorio_5.html")
                html_content += template.render(context)
            
            elif rel_nome == "Relatório 6 - Análise Qualitativa":
                context = {"titulo": rel_nome, "empresa": empresa, "mes": mes, "ano": ano, "analise": dados["Analise"]}
                template = self.env.get_template("relatorio_6.html")
                html_content += template.render(context)
            
            elif rel_nome == "Relatório 7 - Imagens":
                imagens_urls = [self._caminho_para_url(img) for img in dados["Imagens"]]
                logger.info(f"URLs das imagens do Relatório 7: {imagens_urls}")
                context = {"titulo": rel_nome, "empresa": empresa, "mes": mes, "ano": ano, "imagens": imagens_urls}
                template = self.env.get_template("relatorio_7.html")
                html_content += template.render(context)
        
        options = {
            "page-size": "A4",
            "enable-local-file-access": "",
            "allow": [os.path.abspath(self.static_dir)],
            "javascript-delay": "1000"
        }
        
        pdfkit.from_string(html_content, output_path, options=options, configuration=self.config)
        # Save HTML content to file for testing/debugging
        with open("relatorio_teste.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        logger.info(f"PDF gerado em: {output_path}")
        return output_path