from pypdf import PdfWriter, PdfReader
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_marketing_pdfs():
    writer = PdfWriter()
    marketing_paths = [
        "C:\\Users\\gonca\\OneDrive\\Área de Trabalho\\IZE\\Relatório Mensal\\code\\v2_relatorio_mensal\\assets\\images\\pdf_marketing_1.pdf",
        "C:\\Users\\gonca\\OneDrive\\Área de Trabalho\\IZE\\Relatório Mensal\\code\\v2_relatorio_mensal\\assets\\images\\pdf_marketing_2.pdf"
    ]

    for path in marketing_paths:
        if os.path.exists(path):
            reader = PdfReader(path)
            logger.info(f"Arquivo: {path} com {len(reader.pages)} páginas")
            for page in reader.pages:
                writer.add_page(page)
                logger.debug(f"Página adicionada de {path}")
        else:
            logger.warning(f"Arquivo não encontrado: {path}")

    output_path = "outputs/test_marketing.pdf"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        writer.write(f)
    logger.info(f"PDF de teste salvo em: {output_path} com {len(writer.pages)} páginas")

if __name__ == "__main__":
    test_marketing_pdfs()