from flask import Flask, render_template
import os
import json
import random

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

@app.route('/')
def menu():
    return """
    <h1>Escolha um template para visualizar:</h1>
    <ul>
        <li><a href="/relatorio/1">Relatório 1</a></li>
        <li><a href="/relatorio/2">Relatório 2</a></li>
        <li><a href="/relatorio/3">Relatório 3</a></li>
        <li><a href="/relatorio/4">Relatório 4</a></li>
        <li><a href="/relatorio/5">Relatório 5</a></li>
        <li><a href="/relatorio/6">Relatório 6</a></li>
        <li><a href="/relatorio/7">Relatório 7</a></li>
    </ul>
    """

@app.route('/relatorio/<int:num>')
def visualizar_relatorio(num):
    # Dados de exemplo para testes
    dados_exemplo = {
        "Receita Bruta": 45678.90,
        "Entrada Principal": 25678.50,
        "Receita Secundária": 12890.75,
        "Custo Fixo": 15000.00,
        "Custo Variável": 8500.75,
        "Despesa Operacional": 6500.25,
        "Saída Eventual": 3200.45,
        "Lucro Bruto": 22178.15,
        "Empresa": "Empresa Teste",
    }
    
    # Caminho de exemplo para os gráficos
    grafico_url = f"http://localhost:5000/static/graficos/grafico_exemplo.png"
    
    # Renderize o template apropriado
    return render_template(
        f'relatorio_{num}.html',
        empresa="Empresa Teste",
        mes="Abril",
        ano="2025",
        dados=dados_exemplo,
        grafico=grafico_url,
        # Outros dados que possam ser necessários
        analise="Texto de análise de exemplo" if num == 6 else None,
        imagens=["url1", "url2"] if num == 7 else None,
        indicadores={"ROI": 15.2, "Margem": 22.8} if num == 5 else None
    )

if __name__ == '__main__':
    # Crie pasta de gráficos se não existir
    os.makedirs('static/graficos', exist_ok=True)
    
    app.run(debug=True)