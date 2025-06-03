import os
import base64
import json
from jinja2 import Environment, FileSystemLoader

def criar_html_teste_indice(output_file="templates/preview_indice.html"):
    """
    Cria uma versão de teste do template de índice HTML com dados fictícios para visualização.
    
    Args:
        output_file: Caminho onde o HTML de teste será salvo
    """
    # Configurar o ambiente Jinja2
    env = Environment(loader=FileSystemLoader('.'))
    
    # Carregar o template
    template = env.get_template("templates/indice/template.html")
    
    # Carregar ícones e imagens
    icons_dir = os.path.abspath("assets/icons")
    
    # Carregar o logo em PNG para substituir o SVG
    logo_path = os.path.join(icons_dir, "IZE-SIMBOLO-1.png")
    try:
        with open(logo_path, "rb") as f:
            logo_bytes = f.read()
            logo_png_b64 = base64.b64encode(logo_bytes).decode("ascii")
    except Exception as e:
        print(f"Erro ao carregar logo: {str(e)}")
        logo_png_b64 = ""
    
    # Dados fictícios para o template do índice
    dados_teste = {
        "nome": "Cliente Exemplo",
        "Periodo": "Junho/2024",
        "fluxo_caixa": "Sim",
        "dre_gerencial": "Sim",
        "indicador": "Sim",
        "nota_consultor": "Sim",
        "marca": "Sim"
    }

    # Renderizar template
    try:
        # Modificação para usar logo PNG em vez de SVG
        html = template.render(
            data=dados_teste,
            logo_png_b64=logo_png_b64  # Passamos o logo PNG em vez do SVG
        )
        
        # Salvar o HTML para visualização
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"HTML de teste do índice criado com sucesso em: {output_file}")
        print(f"Abra este arquivo no navegador para visualização.")
        return True
    except Exception as e:
        print(f"Erro ao renderizar template do índice: {str(e)}")
        return False

def criar_servidor_teste():
    """
    Inicia um servidor HTTP simples para visualizar o template do índice
    """
    import http.server
    import socketserver
    
    # Criar o HTML de teste
    if not criar_html_teste_indice():
        print("Não foi possível criar o HTML de teste do índice. Servidor não iniciado.")
        return
    
    # Configurar o servidor
    PORT = 8007  # Porta diferente para não conflitar com outros servidores
    Handler = http.server.SimpleHTTPRequestHandler
    
    print(f"Iniciando servidor na porta {PORT}...")
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Servidor rodando em http://localhost:{PORT}")
            print(f"Acesse http://localhost:{PORT}/templates/preview_indice.html para visualizar o índice")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuário.")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Ferramentas de teste para template de índice')
    parser.add_argument('--serve', action='store_true', help='Iniciar servidor HTTP para visualização')
    
    args = parser.parse_args()
    
    if args.serve:
        criar_servidor_teste()
    else:
        criar_html_teste_indice()
        print("Para iniciar um servidor HTTP para testes, use: python indice_test.py --serve")