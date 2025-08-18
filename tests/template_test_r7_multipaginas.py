import os
import base64
import math
from jinja2 import Environment, FileSystemLoader

def criar_html_teste_r7_multipaginas(output_file="templates/preview_r7_multipaginas.html"):
    """
    Cria uma versão de teste do template HTML do Relatório 7 com MUITOS indicadores 
    para forçar o uso de múltiplas páginas e testar o template2.
    
    Args:
        output_file: Caminho onde o HTML de teste será salvo
    """
    # Configurar o ambiente Jinja2
    env = Environment(loader=FileSystemLoader('.'))
    
    # Carregar os templates
    template_principal = env.get_template("templates/relatorio7/template.html")
    template2 = env.get_template("templates/relatorio7/template2.html")
    
    # Carregar ícones e imagens
    icons_dir = os.path.abspath("assets/icons")
    
    # Rodapé
    rodape_path = os.path.join(icons_dir, "rodape.png")
    try:
        with open(rodape_path, "rb") as f:
            icon_bytes = f.read()
            icon_rodape = base64.b64encode(icon_bytes).decode("ascii")
            print(f"Rodapé carregado: {len(icon_bytes)} bytes")
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
        
        # Determinar se é positivo/negativo/neutro
        if cenario_bom_valido and cenario_ruim_valido:
            if valor >= cenario_bom:
                performance = 'positivo'
            elif valor <= cenario_ruim:
                performance = 'negativo'
            else:
                performance = 'neutro'
        else:
            performance = 'positivo' if valor >= 0 else 'negativo'
        
        # Mapear unidades e performance para ícones
        icon_map = {
            'R$': {
                'positivo': 'LOGO-DINHEIRO-VERDE.png',
                'negativo': 'LOGO-DINHEIRO-LARANJA.png',
                'neutro': 'LOGO-DINHEIRO-CINZA.png'
            },
            '%': {
                'positivo': 'LOGO-PERCENTUAL-VERDE.png',
                'negativo': 'LOGO-PERCENTUAL-LARANJA.png',
                'neutro': 'LOGO-PERCENTUAL-CINZA.png'
            },
            'SU': {
                'positivo': 'LOGO-SU-VERDE.png',
                'negativo': 'LOGO-SU-LARANJA.png',
                'neutro': 'LOGO-SU-CINZA.png'
            }
        }
        
        icon_file = icon_map.get(unidade, icon_map['SU']).get(performance, 'LOGO-SU-CINZA.png')
        return carregar_icone(icon_file)
    
    def get_header_color(valor, cenario_bom=None, cenario_ruim=None):
        """Retorna a cor do header baseada na performance"""
        # Verificar se os cenários são válidos (não NaN)
        cenario_bom_valido = cenario_bom is not None and not (isinstance(cenario_bom, float) and math.isnan(cenario_bom))
        cenario_ruim_valido = cenario_ruim is not None and not (isinstance(cenario_ruim, float) and math.isnan(cenario_ruim))
        
        if cenario_bom_valido and cenario_ruim_valido:
            if valor >= cenario_bom:
                return "#009F64"  # Verde
            elif valor <= cenario_ruim:
                return "#E75F00"  # Laranja
            else:
                return "#A5A5A5"  # Cinza
        else:
            return "#009F64" if valor >= 0 else "#E75F00"
    
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

    # CRIAR MUITOS INDICADORES PARA FORÇAR MÚLTIPLAS PÁGINAS (30+ indicadores)
    indicadores_ficticios = [
        # Página 1 (24 indicadores)
        {"categoria": "Faturamento Mensal", "valor": 650000.00, "cenario_bom": 700000.0, "cenario_ruim": 500000.0, "unidade": "R$"},
        {"categoria": "Margem de Contribuição", "valor": 0.42, "cenario_bom": 0.45, "cenario_ruim": 0.35, "unidade": "%"},
        {"categoria": "Ticket Médio", "valor": 2500.00, "cenario_bom": 3000.0, "cenario_ruim": 2000.0, "unidade": "R$"},
        {"categoria": "Número de Clientes", "valor": 260.0, "cenario_bom": 300.0, "cenario_ruim": 200.0, "unidade": "SU"},
        {"categoria": "CAC (Custo de Aquisição)", "valor": 180.00, "cenario_bom": 150.0, "cenario_ruim": 250.0, "unidade": "R$"},
        {"categoria": "LTV (Life Time Value)", "valor": 12000.00, "cenario_bom": 15000.0, "cenario_ruim": 8000.0, "unidade": "R$"},
        {"categoria": "Taxa de Conversão", "valor": 0.045, "cenario_bom": 0.05, "cenario_ruim": 0.03, "unidade": "%"},
        {"categoria": "ROI Marketing", "valor": 3.2, "cenario_bom": 4.0, "cenario_ruim": 2.0, "unidade": "SU"},
        {"categoria": "Churn Rate", "valor": 0.05, "cenario_bom": 0.03, "cenario_ruim": 0.08, "unidade": "%"},
        {"categoria": "Receita Recorrente (MRR)", "valor": 450000.00, "cenario_bom": 500000.0, "cenario_ruim": 350000.0, "unidade": "R$"},
        {"categoria": "EBITDA", "valor": 125000.00, "cenario_bom": 150000.0, "cenario_ruim": 80000.0, "unidade": "R$"},
        {"categoria": "Margem EBITDA", "valor": 0.19, "cenario_bom": 0.22, "cenario_ruim": 0.15, "unidade": "%"},
        {"categoria": "Crescimento MoM", "valor": 0.08, "cenario_bom": 0.12, "cenario_ruim": 0.03, "unidade": "%"},
        {"categoria": "Leads Qualificados", "valor": 85.0, "cenario_bom": 100.0, "cenario_ruim": 60.0, "unidade": "SU"},
        {"categoria": "Net Promoter Score", "valor": 67.0, "cenario_bom": 70.0, "cenario_ruim": 50.0, "unidade": "SU"},
        {"categoria": "Tempo Médio de Resposta", "valor": 2.5, "cenario_bom": 2.0, "cenario_ruim": 4.0, "unidade": "SU"},
        {"categoria": "Taxa de Retenção", "valor": 0.85, "cenario_bom": 0.90, "cenario_ruim": 0.75, "unidade": "%"},
        {"categoria": "Custo por Lead", "valor": 45.00, "cenario_bom": 40.0, "cenario_ruim": 60.0, "unidade": "R$"},
        {"categoria": "Vendas por Vendedor", "valor": 32500.00, "cenario_bom": 40000.0, "cenario_ruim": 25000.0, "unidade": "R$"},
        {"categoria": "Ciclo de Vendas (dias)", "valor": 18.0, "cenario_bom": 15.0, "cenario_ruim": 25.0, "unidade": "SU"},
        {"categoria": "Taxa de Upsell", "valor": 0.25, "cenario_bom": 0.30, "cenario_ruim": 0.15, "unidade": "%"},
        {"categoria": "Satisfação do Cliente", "valor": 8.2, "cenario_bom": 9.0, "cenario_ruim": 7.0, "unidade": "SU"},
        {"categoria": "Produtividade por Funcionário", "valor": 85000.00, "cenario_bom": 100000.0, "cenario_ruim": 65000.0, "unidade": "R$"},
        {"categoria": "Margem Bruta", "valor": 0.65, "cenario_bom": 0.70, "cenario_ruim": 0.55, "unidade": "%"},
        
        # Página 2 (mais 10 indicadores para testar)
        {"categoria": "Índice de Liquidez Corrente", "valor": 1.8, "cenario_bom": 2.0, "cenario_ruim": 1.2, "unidade": "SU"},
        {"categoria": "Giro de Estoque", "valor": 6.5, "cenario_bom": 8.0, "cenario_ruim": 4.0, "unidade": "SU"},
        {"categoria": "Prazo Médio de Recebimento", "valor": 35.0, "cenario_bom": 30.0, "cenario_ruim": 45.0, "unidade": "SU"},
        {"categoria": "Endividamento Total", "valor": 0.35, "cenario_bom": 0.25, "cenario_ruim": 0.50, "unidade": "%"},
        {"categoria": "ROE (Return on Equity)", "valor": 0.18, "cenario_bom": 0.22, "cenario_ruim": 0.12, "unidade": "%"},
        {"categoria": "ROA (Return on Assets)", "valor": 0.12, "cenario_bom": 0.15, "cenario_ruim": 0.08, "unidade": "%"},
        {"categoria": "Turnover de Funcionários", "valor": 0.08, "cenario_bom": 0.05, "cenario_ruim": 0.15, "unidade": "%"},
        {"categoria": "Investimento em P&D", "valor": 25000.00, "cenario_bom": 30000.0, "cenario_ruim": 15000.0, "unidade": "R$"},
        {"categoria": "Market Share", "valor": 0.12, "cenario_bom": 0.15, "cenario_ruim": 0.08, "unidade": "%"},
        {"categoria": "Eficiência Operacional", "valor": 0.78, "cenario_bom": 0.85, "cenario_ruim": 0.65, "unidade": "%"}
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
            'header_color': get_header_color(valor, cenario_bom, cenario_ruim),
            'nome_font_size': sizes['nome_font_size'],
            'text_top': sizes['text_top'],
            'valor_font_size': sizes['valor_font_size'],
            'cenario_font_size': sizes['cenario_font_size']
        }
        indicadores_processados.append(indicador_processado)

    # SIMULAR LÓGICA DE MÚLTIPLAS PÁGINAS
    indicadores_por_pagina = 24
    total_indicadores = len(indicadores_processados)
    
    print(f"Total de indicadores: {total_indicadores}")
    print(f"Indicadores por página: {indicadores_por_pagina}")
    print(f"Páginas necessárias: {math.ceil(total_indicadores / indicadores_por_pagina)}")
    
    # Dividir em páginas
    primeira_pagina = indicadores_processados[:indicadores_por_pagina]
    indicadores_restantes = indicadores_processados[indicadores_por_pagina:]
    
    total_paginas = math.ceil(total_indicadores / indicadores_por_pagina)
    
    # RENDERIZAR PRIMEIRA PÁGINA (template principal)
    print("Renderizando primeira página com template principal...")
    paginas_primeira = [{
        'indicadores': primeira_pagina,
        'numero_pagina': 1,
        'total_paginas': total_paginas,
        'eh_primeira_pagina': True,
        'eh_ultima_pagina': total_paginas == 1
    }]
    
    template_data_primeira = {
        "nome": "Cliente Teste Múltiplas Páginas",
        "Periodo": "Teste/2025",
        "sem_indicadores": False,
        "paginas": paginas_primeira,
        "total_indicadores": len(primeira_pagina)
    }
    
    html_primeira_pagina = template_principal.render(
        data=template_data_primeira,
        icon_rodape=icon_rodape,
        cliente_nome="Cliente Teste Múltiplas Páginas",
        mes_nome="Teste",
        ano=2025
    )
    
    # RENDERIZAR PÁGINAS SUBSEQUENTES (template2)
    html_completo = html_primeira_pagina
    
    for pagina_num in range(2, total_paginas + 1):
        print(f"Renderizando página {pagina_num} com template2...")
        inicio_idx = (pagina_num - 2) * indicadores_por_pagina
        fim_idx = inicio_idx + indicadores_por_pagina
        indicadores_pagina = indicadores_restantes[inicio_idx:fim_idx]
        
        print(f"  - Página {pagina_num}: {len(indicadores_pagina)} indicadores")
        
        html_pagina = template2.render(
            indicadores=indicadores_pagina,
            nome_relatorio="Cliente Teste Múltiplas Páginas",
            periodo="Teste/2025",
            icon_rodape=icon_rodape
        )
        
        html_completo += html_pagina

    try:
        # Salvar o HTML para visualização
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_completo)
        
        print(f"HTML de teste do Relatório 7 (múltiplas páginas) criado com sucesso em: {output_file}")
        print(f"Total de páginas: {total_paginas}")
        print(f"Página 1: {len(primeira_pagina)} indicadores (template principal)")
        
        for i, pagina_num in enumerate(range(2, total_paginas + 1), 1):
            inicio_idx = (i - 1) * indicadores_por_pagina
            fim_idx = inicio_idx + indicadores_por_pagina
            indicadores_count = len(indicadores_restantes[inicio_idx:fim_idx])
            print(f"Página {pagina_num}: {indicadores_count} indicadores (template2)")
        
        print(f"Abra este arquivo no navegador para visualização.")
        return True
    except Exception as e:
        print(f"Erro ao renderizar template do Relatório 7: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def criar_servidor_teste():
    """
    Inicia um servidor HTTP simples para visualizar o template
    """
    import http.server
    import socketserver
    
    # Criar o HTML de teste
    if not criar_html_teste_r7_multipaginas():
        print("Não foi possível criar o HTML de teste. Servidor não iniciado.")
        return
    
    # Configurar o servidor
    PORT = 8007
    Handler = http.server.SimpleHTTPRequestHandler
    
    print(f"Iniciando servidor na porta {PORT}...")
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Servidor rodando em http://localhost:{PORT}")
            print(f"Acesse http://localhost:{PORT}/templates/preview_r7_multipaginas.html para visualizar")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuário.")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Teste do template do Relatório 7 com múltiplas páginas')
    parser.add_argument('--serve', action='store_true', help='Iniciar servidor HTTP para visualização')
    
    args = parser.parse_args()
    
    if args.serve:
        criar_servidor_teste()
    else:
        criar_html_teste_r7_multipaginas()
        print("Para iniciar um servidor HTTP para testes, use: python tests/template_test_r7_multipaginas.py --serve")