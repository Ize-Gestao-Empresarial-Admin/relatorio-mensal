import os
import base64
import json
import math
from jinja2 import Environment, FileSystemLoader

def criar_html_teste_r7(output_file="templates/preview_r7.html"):
    """
    Cria uma versão de teste do template HTML do Relatório 7 com dados fictícios para visualização.
    
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
    template = env.get_template("templates/relatorio7/template.html")
    
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
    
    # Função auxiliar para carregar ícones específicos
    def carregar_icone(nome_arquivo):
        icon_path = os.path.join(icons_dir, nome_arquivo)
        try:
            with open(icon_path, "rb") as f:
                return base64.b64encode(f.read()).decode("ascii")
        except Exception as e:
            print(f"Erro ao carregar ícone {nome_arquivo}: {str(e)}")
            return ""

    # Função para simular a lógica do renderer
    def get_icon_base64(unidade, valor, cenario_bom=None, cenario_ruim=None):
        """Simula a lógica de seleção de ícones do renderer"""
        # Verificar se os cenários são válidos (não NaN)
        cenario_bom_valido = cenario_bom is not None and not (isinstance(cenario_bom, float) and math.isnan(cenario_bom))
        cenario_ruim_valido = cenario_ruim is not None and not (isinstance(cenario_ruim, float) and math.isnan(cenario_ruim))
        
        # Determinar se é positivo/negativo
        is_positive = True
        if cenario_bom_valido and cenario_ruim_valido:
            if valor >= cenario_bom:
                is_positive = True
            elif valor <= cenario_ruim:
                is_positive = False
            else:
                is_positive = valor >= 0
        else:
            is_positive = valor >= 0
        
        # Mapear unidades para ícones
        icon_map = {
            'R$': 'LOGO-DINHEIRO-VERDE.png' if is_positive else 'LOGO-DINHEIRO-LARANJA.png',
            '%': 'LOGO-PERCENTUAL-VERDE.png' if is_positive else 'LOGO-PERCENTUAL-LARANJA.png',
            'SU': 'LOGO-SU-VERDE.png' if is_positive else 'LOGO-SU-LARANJA.png'
        }
        
        icon_file = icon_map.get(unidade, 'LOGO-SU-VERDE.png')
        return carregar_icone(icon_file)

    def format_cenario_text(bom, ruim, unidade):
        """Formata o texto de cenário bom/ruim"""
        # Verificar se os valores são válidos (não NaN)
        bom_valido = bom is not None and not (isinstance(bom, float) and math.isnan(bom))
        ruim_valido = ruim is not None and not (isinstance(ruim, float) and math.isnan(ruim))
        
        if not bom_valido or not ruim_valido:
            return "Cenário não definido"
        
        # Formatação baseada na unidade
        if unidade == 'R$':
            bom_fmt = f"R$ {bom:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ruim_fmt = f"R$ {ruim:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        elif unidade == '%':
            bom_fmt = f"{bom * 100:.2f}%".replace(".", ",")
            ruim_fmt = f"{ruim * 100:.2f}%".replace(".", ",")
        else:  # SU
            bom_fmt = f"{bom:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ruim_fmt = f"{ruim:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        return f"O cenário bom é {bom_fmt} e o ruim é {ruim_fmt}"

    def calculate_dynamic_sizes(nome, valor, bom=None):
        """Calcula tamanhos dinâmicos para nome e valor"""
        nome_length = len(nome)
        
        # Tamanho da fonte e posição do texto baseado no comprimento do nome
        if nome_length > 60:
            nome_font_size = "12px"
            text_top = "17px"
        elif nome_length > 40:
            nome_font_size = "13px" 
            text_top = "20px"
        else:
            nome_font_size = "16px"
            text_top = "27px"
        
        # Tamanho da fonte do valor baseado no tamanho do número
        valor_font_size = "15px" if abs(valor) >= 999999999 else "18px"
        
        # Tamanho da fonte do cenário baseado no valor do "bom"
        if bom is not None and not (isinstance(bom, float) and math.isnan(bom)):
            cenario_font_size = "7px" if bom >= 10000000 else "8px"
        else:
            cenario_font_size = "8px"
        
        return {
            'nome_font_size': nome_font_size,
            'text_top': text_top,
            'valor_font_size': valor_font_size,
            'cenario_font_size': cenario_font_size
        }

    # Dados fictícios para o template do Relatório 7
    indicadores_ficticios = [
        {
            "categoria": "Faturamento",
            "valor": 934387.91,
            "cenario_bom": 1000000.0,
            "cenario_ruim": 500000.0,
            "unidade": "R$"
        },
        {
            "categoria": "Margem de Contribuição (Lucro Bruto)",
            "valor": 415505.30,
            "cenario_bom": 450000.0,
            "cenario_ruim": 300000.0,
            "unidade": "R$"
        },
        {
            "categoria": "Lucro Líquido",
            "valor": 75740.03,
            "cenario_bom": 100000.0,
            "cenario_ruim": 50000.0,
            "unidade": "R$"
        },
        {
            "categoria": "Geração de Caixa",
            "valor": 83631.08,
            "cenario_bom": 90000.0,
            "cenario_ruim": 40000.0,
            "unidade": "R$"
        },
        {
            "categoria": "CAC",
            "valor": 6038.36,
            "cenario_bom": 5000.0,
            "cenario_ruim": 8000.0,
            "unidade": "R$"
        },
        {
            "categoria": "Crescimento do Mês",
            "valor": 0.3498,
            "cenario_bom": 0.25,
            "cenario_ruim": 0.05,
            "unidade": "%"
        },
        {
            "categoria": "% Investimentos",
            "valor": -0.0677,
            "cenario_bom": -0.05,
            "cenario_ruim": -0.15,
            "unidade": "%"
        },
        {
            "categoria": "Quantidade de Clientes",
            "valor": 38.0,
            "cenario_bom": 50.0,
            "cenario_ruim": 20.0,
            "unidade": "SU"
        },
        {
            "categoria": "Quantidade de Cotas",
            "valor": 93.0,
            "cenario_bom": 100.0,
            "cenario_ruim": 50.0,
            "unidade": "SU"
        },
        {
            "categoria": "Ticket Médio – Clientes",
            "valor": 634062.97,
            "cenario_bom": 700000.0,
            "cenario_ruim": 400000.0,
            "unidade": "R$"
        },
        {
            "categoria": "PE Líquido",
            "valor": 1047273.08,
            "cenario_bom": 1200000.0,
            "cenario_ruim": 800000.0,
            "unidade": "R$"
        },
        {
            "categoria": "CAC/Ticket Médio Clientes",
            "valor": 0.0095,
            "cenario_bom": 0.008,
            "cenario_ruim": 0.015,
            "unidade": "%"
        }
    ]

    # Processar indicadores (simulando o que o renderer faz)
    indicadores_processados = []
    for indicador in indicadores_ficticios:
        nome = indicador['categoria']
        valor = indicador['valor']
        unidade = indicador['unidade']
        cenario_bom = indicador['cenario_bom']
        cenario_ruim = indicador['cenario_ruim']
        
        # Calcular tamanhos dinâmicos
        sizes = calculate_dynamic_sizes(nome, valor, cenario_bom)
        
        # Processar dados do indicador
        indicador_processado = {
            'nome': nome,
            'valor': valor,
            'unidade': unidade,
            'cenario_bom': cenario_bom,
            'cenario_ruim': cenario_ruim,
            'cenario_texto': format_cenario_text(cenario_bom, cenario_ruim, unidade),
            'icon_base64': get_icon_base64(unidade, valor, cenario_bom, cenario_ruim),
            'nome_font_size': sizes['nome_font_size'],
            'text_top': sizes['text_top'],
            'valor_font_size': sizes['valor_font_size'],
            'cenario_font_size': sizes['cenario_font_size']
        }
        indicadores_processados.append(indicador_processado)

    # Dados para o template
    dados_teste = {
        "nome": "Cliente Teste Indicadores",
        "Periodo": "Abril/2025",
        "notas": "Este é um exemplo de notas para o Relatório 7 de Indicadores Operacionais.\n\nOs indicadores apresentados fornecem uma visão abrangente do desempenho operacional da empresa. Os cenários 'bom' e 'ruim' representam parâmetros de referência para avaliação dos resultados.\n\nValores próximos ao cenário bom indicam performance positiva, enquanto valores próximos ao cenário ruim sugerem necessidade de atenção e possíveis ações corretivas.",
        "indicadores": indicadores_processados
    }

    # Renderizar template
    try:
        html = template.render(
            data=dados_teste,
            icon_rodape=icon_rodape,
            cliente_nome="Cliente Teste Indicadores",
            mes_nome="Abril",
            ano=2025
        )
        
        # Salvar o HTML para visualização
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"HTML de teste do Relatório 7 criado com sucesso em: {output_file}")
        print(f"Abra este arquivo no navegador para visualização.")
        return True
    except Exception as e:
        print(f"Erro ao renderizar template do Relatório 7: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def criar_dados_json_teste():
    """Cria um arquivo JSON com dados de teste para referência"""
    dados_json = {
        "relatorio_7_dados_teste": [
            {
                "categoria": "Faturamento",
                "valor": 934387.91,
                "cenario_bom": 1000000.0,
                "cenario_ruim": 500000.0,
                "unidade": "R$"
            },
            {
                "categoria": "Margem de Contribuição (Lucro Bruto)",
                "valor": 415505.30,
                "cenario_bom": 450000.0,
                "cenario_ruim": 300000.0,
                "unidade": "R$"
            },
            {
                "categoria": "Lucro Líquido",
                "valor": 75740.03,
                "cenario_bom": 100000.0,
                "cenario_ruim": 50000.0,
                "unidade": "R$"
            },
            {
                "categoria": "Crescimento do Mês",
                "valor": 0.3498,
                "cenario_bom": 0.25,
                "cenario_ruim": 0.05,
                "unidade": "%"
            },
            {
                "categoria": "Quantidade de Clientes",
                "valor": 38.0,
                "cenario_bom": 50.0,
                "cenario_ruim": 20.0,
                "unidade": "SU"
            }
        ],
        "notas": "Os indicadores apresentados fornecem uma visão abrangente do desempenho operacional da empresa."
    }
    
    with open("templates/dados_teste_r7.json", 'w', encoding='utf-8') as f:
        json.dump(dados_json, f, indent=2, ensure_ascii=False)
    
    print("Arquivo JSON de dados de teste criado: templates/dados_teste_r7.json")

def criar_servidor_teste_r7():
    """
    Inicia um servidor HTTP simples para visualizar o template do Relatório 7
    """
    import http.server
    import socketserver
    
    # Criar o HTML de teste
    if not criar_html_teste_r7():
        print("Não foi possível criar o HTML de teste. Servidor não iniciado.")
        return
    
    # Configurar o servidor
    PORT = 8007
    Handler = http.server.SimpleHTTPRequestHandler
    
    print(f"Iniciando servidor na porta {PORT}...")
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Servidor rodando em http://localhost:{PORT}")
            print(f"Acesse http://localhost:{PORT}/templates/preview_r7.html para visualizar o Relatório 7")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuário.")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {str(e)}")

def testar_todos_indicadores():
    """
    Testa diferentes combinações de indicadores para verificar o layout
    """
    # Testa com nomes muito longos
    print("Testando com nomes longos...")
    criar_html_teste_r7("templates/preview_r7_nomes_longos.html")
    
    # Criar dados JSON de teste
    criar_dados_json_teste()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Ferramentas de teste para template do Relatório 7')
    parser.add_argument('--serve', action='store_true', help='Iniciar servidor HTTP para visualização')
    parser.add_argument('--json', action='store_true', help='Criar arquivo JSON com dados de teste')
    parser.add_argument('--all', action='store_true', help='Testar todas as variações')
    
    args = parser.parse_args()
    
    if args.serve:
        criar_servidor_teste_r7()
    elif args.json:
        criar_dados_json_teste()
    elif args.all:
        testar_todos_indicadores()
    else:
        criar_html_teste_r7()
        print("Para iniciar um servidor HTTP para testes, use: python template_test_r7.py --serve")
        print("Para criar dados JSON de teste: python template_test_r7.py --json")
        print("Para testar todas as variações: python template_test_r7.py --all")