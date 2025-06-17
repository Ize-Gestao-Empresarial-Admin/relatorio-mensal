import os
import base64
import json
from jinja2 import Environment, FileSystemLoader

def criar_html_teste(output_file="templates/preview.html"):
    """
    Cria uma versão de teste do template HTML com dados fictícios para visualização.
    
    Args:
        output_file: Caminho onde o HTML de teste será salvo
    """
    # Configurar o ambiente Jinja2
    env = Environment(loader=FileSystemLoader('.'))
    
    # Registrar os filtros personalizados
    def format_currency(value):
        if value is None:
            return "R$ 0,00"
        try:
            return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return value
    
    def format_percentage(value):
        if value is None:
            return "0%"
        try:
            return f"{value:.1%}".replace(".", ",")
        except:
            return value
    
    def format_number(value, decimal_places=2):
        if value is None:
            return "0"
        try:
            format_str = f"{{:.{decimal_places}f}}"
            return format_str.format(value).replace(".", ",")
        except:
            return value
    
    # Adicionar os filtros ao ambiente
    env.filters['format_currency'] = format_currency
    env.filters['format_percentage'] = format_percentage
    env.filters['format_number'] = format_number
    
    # Carregar o template
    template = env.get_template("templates/relatorio1/template.html")
    
    # Carregar ícones e imagens
    icons_dir = os.path.abspath("assets/icons")
    
    # Rodapé
    rodape_path = os.path.join(icons_dir, "rodape.png")
    try:
        with open(rodape_path, "rb") as f:
            icon_bytes = f.read()
            icon_rodape = base64.b64encode(icon_bytes).decode("ascii")
    except Exception as e:
        print(f"Erro ao carregar rodapé: {str(e)}")
        icon_rodape = ""
    
    # Setas
    seta_up_verde_path = os.path.join(icons_dir, "SETA-UP-VERDE.svg")
    with open(seta_up_verde_path, "rb") as f:
        seta_up_verde_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    seta_down_laranja_path = os.path.join(icons_dir, "SETA-DOWN-LARANJA.svg")
    with open(seta_down_laranja_path, "rb") as f:
        seta_down_laranja_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    seta_up_laranja_path = os.path.join(icons_dir, "SETA-UP-LARANJA.svg")
    with open(seta_up_laranja_path, "rb") as f:
        seta_up_laranja_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    seta_down_verde_path = os.path.join(icons_dir, "SETA-DOWN-VERDE.svg")
    with open(seta_down_verde_path, "rb") as f:
        seta_down_verde_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Dados fictícios para o template
    dados_teste = {
        "nome": "Cliente Exemplo",
        "Periodo": "Junho/2024",
        "notas": "Estas são notas fictícias para testar a formatação e o layout do documento. \nO formato do texto respeita quebras de linha e espaçamento. \n\nAs receitas deste mês apresentaram crescimento em relação ao período anterior, principalmente nas categorias de Vendas Online e Consultoria.",
        "receita": 125000.50,
        "represent_receita": 100.0,
        "receita_categories": [
            {
                "name": "Vendas Online",
                "value": 75000.00,
                "representatividade": 0.60,
                "variacao": 0.25,
                "barra_rep": 60.0
            },
            {
                "name": "Consultoria",
                "value": 35000.00,
                "representatividade": 0.28,
                "variacao": 0.15,
                "barra_rep": 28.0
            },
            {
                "name": "Serviços Complementares",
                "value": 15000.50,
                "representatividade": 0.12,
                "variacao": -0.05,
                "barra_rep": 12.0
            }
        ],
        "custos": 50000.00,
        "represent_custos": 40.0,
        "custo_categories": [
            {
                "name": "Custos com Marketing",
                "value": 25000.00,
                "representatividade": 0.50,
                "variacao": 0.10,
                "barra_rep": 50.0
            },
            {
                "name": "Custos Operacionais",
                "value": 15000.00,
                "representatividade": 0.30,
                "variacao": -0.08,
                "barra_rep": 30.0
            },
            {
                "name": "Comissões",
                "value": 10000.00,
                "representatividade": 0.20,
                "variacao": 0.05,
                "barra_rep": 20.0
            }
        ]
    }

    # Renderizar template
    try:
        html = template.render(
            data=dados_teste,
            icon_rodape=icon_rodape,
            seta_b64=seta_up_verde_b64,
            seta_b64_2=seta_down_laranja_b64,
            seta_b64_3=seta_up_laranja_b64,
            seta_b64_4=seta_down_verde_b64,
            cliente_nome="Cliente Exemplo",
            mes_nome="Junho",
            ano=2024
        )
        
        # Salvar o HTML para visualização
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"HTML de teste criado com sucesso em: {output_file}")
        print(f"Abra este arquivo no navegador para visualização.")
        return True
    except Exception as e:
        print(f"Erro ao renderizar template: {str(e)}")
        return False

def testar_todos_templates():
    """
    Cria versões de teste para todos os templates de relatório
    """
    # Lista de todos os templates disponíveis
    templates = [1, 2, 3, 4, 6, 7, 8]  # Ajuste conforme necessário
    
    for num in templates:
        try:
            output_file = f"templates/preview_relatorio{num}.html"
            template_file = f"templates/relatorio{num}/template.html"
            
            # Verificar se o template existe
            if not os.path.exists(template_file):
                print(f"Template {template_file} não encontrado, pulando...")
                continue
                
            # Aqui você adicionaria lógica específica para cada template
            # Por enquanto, apenas criamos o do relatório 1
            if num == 1:
                criar_html_teste(output_file)
            
        except Exception as e:
            print(f"Erro ao processar template {num}: {str(e)}")

def criar_servidor_teste():
    """
    Inicia um servidor HTTP simples para visualizar os templates
    """
    import http.server
    import socketserver
    
    # Criar o HTML de teste
    if not criar_html_teste():
        print("Não foi possível criar o HTML de teste. Servidor não iniciado.")
        return
    
    # Configurar o servidor
    PORT = 8006
    Handler = http.server.SimpleHTTPRequestHandler
    
    print(f"Iniciando servidor na porta {PORT}...")
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Servidor rodando em http://localhost:{PORT}")
            print(f"Acesse http://localhost:{PORT}/templates/preview.html para visualizar o relatório 1")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuário.")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Ferramentas de teste para templates de relatório')
    parser.add_argument('--serve', action='store_true', help='Iniciar servidor HTTP para visualização')
    parser.add_argument('--template', type=int, help='Número do template específico para testar')
    parser.add_argument('--all', action='store_true', help='Testar todos os templates')
    
    args = parser.parse_args()
    
    if args.serve:
        criar_servidor_teste()
    elif args.template:
        criar_html_teste(f"templates/preview_relatorio{args.template}.html")
    elif args.all:
        testar_todos_templates()
    else:
        criar_html_teste()
        print("Para iniciar um servidor HTTP para testes, use: python template_test.py --serve")
        print("Para testar um template específico: python template_test.py --template <número>")