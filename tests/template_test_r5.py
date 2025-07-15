import os
import base64
import json
from jinja2 import Environment, FileSystemLoader

def criar_html_teste_relatorio5(output_file="templates/preview_relatorio5.html", valor_geracao=350000.00):
    """
    Cria uma versão de teste do template HTML do Relatório 5 com dados fictícios para visualização.
    
    Args:
        output_file: Caminho onde o HTML de teste será salvo
        valor_geracao: Valor para a geração de caixa (positivo ou negativo)
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
    template = env.get_template("templates/relatorio5/template.html")
    
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

    # Dados fictícios para o Relatório 5
    dados_teste = {
        "nome": "Cliente Exemplo",
        "Periodo": "Junho/2024",
        "notas": "Estas são notas fictícias para testar a formatação do Relatório 5.\n\nA Geração de Caixa representa o resultado financeiro do período, considerando os fluxos de entrada e saída de recursos.\n\nAs categorias apresentadas mostram os principais componentes desta geração.",
        
        # Geração de Caixa
        "geracao_de_caixa": valor_geracao,
        "represent_geracao_de_caixa": 100.0,
        "geracao_de_caixa_categories": [
            {
                "name": "Receitas Operacionais",
                "value": abs(valor_geracao * 0.65),
                "representatividade": 0.65,
                "variacao": 0.18,
                "barra_rep": 65.0
            },
            {
                "name": "Receitas Não Operacionais",
                "value": abs(valor_geracao * 0.20),
                "representatividade": 0.20,
                "variacao": 0.05,
                "barra_rep": 20.0
            },
            {
                "name": "Recuperação de Ativos",
                "value": abs(valor_geracao * 0.15),
                "representatividade": 0.15,
                "variacao": -0.03,
                "barra_rep": 15.0
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
            cliente_nome="Cliente Exemplo",
            mes_nome="Junho",
            ano=2024
        )
        
        # Salvar o HTML para visualização
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"HTML de teste do Relatório 5 criado com sucesso em: {output_file}")
        print(f"Abra este arquivo no navegador para visualização.")
        return True
    except Exception as e:
        print(f"Erro ao renderizar template do Relatório 5: {str(e)}")
        return False

def criar_servidor_teste():
    """
    Inicia um servidor HTTP simples para visualizar o template do Relatório 5
    """
    import http.server
    import socketserver
    
    # Criar o HTML de teste com valor positivo
    if not criar_html_teste_relatorio5(output_file="templates/preview_relatorio5_positivo.html", valor_geracao=350000.00):
        print("Não foi possível criar o HTML de teste com valor positivo.")
    
    # Criar o HTML de teste com valor negativo 
    if not criar_html_teste_relatorio5(output_file="templates/preview_relatorio5_negativo.html", valor_geracao=-150000.00):
        print("Não foi possível criar o HTML de teste com valor negativo.")
    
    # Configurar o servidor
    PORT = 8007  # Porta diferente da usada para o Relatório 4
    Handler = http.server.SimpleHTTPRequestHandler
    
    print(f"Iniciando servidor na porta {PORT}...")
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Servidor rodando em http://localhost:{PORT}")
            print(f"Acesse http://localhost:{PORT}/templates/preview_relatorio5_positivo.html para visualizar com valor positivo")
            print(f"Acesse http://localhost:{PORT}/templates/preview_relatorio5_negativo.html para visualizar com valor negativo")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuário.")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Ferramentas de teste para o template do Relatório 5')
    parser.add_argument('--serve', action='store_true', help='Iniciar servidor HTTP para visualização')
    parser.add_argument('--positive', action='store_true', help='Gerar exemplo com valor positivo')
    parser.add_argument('--negative', action='store_true', help='Gerar exemplo com valor negativo')
    
    args = parser.parse_args()
    
    if args.serve:
        criar_servidor_teste()
    elif args.positive:
        criar_html_teste_relatorio5(valor_geracao=350000.00)
    elif args.negative:
        criar_html_teste_relatorio5(valor_geracao=-150000.00)
    else:
        # Por padrão, cria exemplos para ambos os casos
        criar_html_teste_relatorio5(output_file="templates/preview_relatorio5_positivo.html", valor_geracao=350000.00)
        criar_html_teste_relatorio5(output_file="templates/preview_relatorio5_negativo.html", valor_geracao=-150000.00)
        print("Para iniciar um servidor HTTP para testes, use: python template_test_r5.py --serve")
        print("Para gerar apenas o exemplo positivo: python template_test_r5.py --positive")
        print("Para gerar apenas o exemplo negativo: python template_test_r5.py --negative")