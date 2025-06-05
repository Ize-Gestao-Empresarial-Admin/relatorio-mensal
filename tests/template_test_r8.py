import os
import base64
from jinja2 import Environment, FileSystemLoader

def criar_html_teste_r8(output_file="templates/preview_relatorio8.html"):
    """
    Cria uma versão de teste do template HTML do Relatório 8 (Nota do Consultor) 
    com dados fictícios para visualização.
    
    Args:
        output_file: Caminho onde o HTML de teste será salvo
    """
    # Configurar o ambiente Jinja2
    env = Environment(loader=FileSystemLoader('.'))
    
    # Carregar o template
    template = env.get_template("templates/relatorio8/template.html")
    
    # Carregar ícones e imagens
    icons_dir = os.path.abspath("assets/icons")
    
    # Rodapé
    rodape_path = os.path.join(icons_dir, "rodape.png")
    try:
        with open(rodape_path, "rb") as f:
            icon_bytes = f.read()
            icon_rodape = base64.b64encode(icon_bytes).decode("ascii")
            print(f"Rodapé carregado com sucesso: {len(icon_bytes)} bytes")
    except Exception as e:
        print(f"Erro ao carregar rodapé: {str(e)}")
        icon_rodape = ""

    # Criar conteúdo HTML para teste com formatação rica
    nota_consultor_html = """
    <p><strong>Análise Geral do Período</strong></p>
    <p>O cliente apresentou melhoria significativa nos indicadores financeiros durante o mês de junho/2024, com destaque para:</p>
    <ul>
        <li>Aumento de 15% na receita bruta comparada ao mesmo período do ano anterior</li>
        <li>Redução de 8% nos custos fixos</li>
        <li>Margem de contribuição de 42%, representando um aumento de 3 pontos percentuais</li>
    </ul>
    <p>&nbsp;</p>
    <p><strong>Pontos de Atenção</strong></p>
    <p>É necessário monitorar o fluxo de caixa para os próximos meses, considerando:</p>
    <ol>
        <li>O aumento significativo nas despesas com marketing</li>
        <li>A sazonalidade do terceiro trimestre, historicamente mais fraca</li>
        <li>O investimento previsto em nova linha de produtos</li>
    </ol>
    <p>&nbsp;</p>
    <p><strong>Recomendações</strong></p>
    <p>Recomendamos as seguintes ações para o próximo período:</p>
    <ul>
        <li>Revisão da política de descontos para clientes recorrentes</li>
        <li>Análise da efetividade dos canais de marketing digital</li>
        <li>Planejamento antecipado para o período de baixa demanda</li>
    </ul>
    <p>&nbsp;</p>
    <p><em>Este parecer técnico foi elaborado com base nos dados financeiros fornecidos pela empresa e nas análises realizadas pela nossa equipe de consultoria.</em></p>
    """

    # Dados fictícios para o template
    dados_teste = {
        "nome": "Cliente Exemplo",
        "Periodo": "Junho/2024",
        "nota_consultor": nota_consultor_html
    }

    # Renderizar template
    try:
        html = template.render(
            data=dados_teste,
            icon_rodape=icon_rodape,
            cliente_nome="Cliente Exemplo",
            mes_nome="Junho",
            ano=2024
        )
        
        # Salvar o HTML para visualização
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"HTML de teste para Relatório 8 criado com sucesso em: {output_file}")
        print(f"Abra este arquivo no navegador para visualização.")
        return True
    except Exception as e:
        print(f"Erro ao renderizar template: {str(e)}")
        return False

def criar_servidor_teste():
    """
    Inicia um servidor HTTP simples para visualizar o template
    """
    import http.server
    import socketserver
    
    # Criar o HTML de teste
    if not criar_html_teste_r8():
        print("Não foi possível criar o HTML de teste. Servidor não iniciado.")
        return
    
    # Configurar o servidor
    PORT = 8008
    Handler = http.server.SimpleHTTPRequestHandler
    
    print(f"Iniciando servidor na porta {PORT}...")
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Servidor rodando em http://localhost:{PORT}")
            print(f"Acesse http://localhost:{PORT}/templates/preview_relatorio8.html para visualizar o relatório 8")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuário.")
    except Exception as e:
        print(f"Erro ao iniciar servidor: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Teste do template do Relatório 8 - Nota do Consultor')
    parser.add_argument('--serve', action='store_true', help='Iniciar servidor HTTP para visualização')
    
    args = parser.parse_args()
    
    if args.serve:
        criar_servidor_teste()
    else:
        criar_html_teste_r8()
        print("Para iniciar um servidor HTTP para testes, use: python template_test_r8.py --serve")