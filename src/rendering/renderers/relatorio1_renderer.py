# src/rendering/renderers/relatorio1_renderer.py
from typing import Dict, Any, List, Tuple, Union
from src.rendering.renderers.base_renderer import BaseRenderer
import os
import base64

class Relatorio1Renderer(BaseRenderer):
    """
    Renderizador para o Relatório 1 - Análise do Fluxo de Caixa.
    Converte os dados do relatório em HTML para posterior geração de PDF.
    """
    
    def render(self, data: Union[List[Dict[str, Any]], Tuple[List[Dict[str, Any]], Dict[str, str]]], 
               cliente_nome: str, mes_nome: str, ano: int) -> str:
        """
        Renderiza os dados do Relatório 1 em HTML.
        
        Args:
            data: Dados do relatório ou tupla (dados, notas)
            cliente_nome: Nome do cliente
            mes_nome: Nome do mês
            ano: Ano do relatório
            
        Returns:
            HTML formatado
        """
        # Extrair dados na estrutura correta
        if isinstance(data, tuple) and len(data) == 2:
            relatorio_data = data[0]
            notas = data[1].get("notas", "")
        else:
            relatorio_data = data
            notas = ""
        
        # Carregar SVGs para os ícones
        icons_dir = os.path.abspath("assets/icons")
        
        # Logo
        logo_path = os.path.join(icons_dir, "IZE-LOGO-2.svg")
        with open(logo_path, "r", encoding="utf-8") as f:
            logo_svg = f.read()
        
        # Setas (carregar como base64)
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
        
        # Processar dados do relatório
        # Estrutura: [{'categoria': 'Receitas', 'valor': X, 'subcategorias': [...]}, {'categoria': 'Custos Variáveis', ...}]
        receitas_data = next((item for item in relatorio_data if item['categoria'] == 'Receitas'), {})
        custos_data = next((item for item in relatorio_data if item['categoria'] == 'Custos Variáveis'), {})

        # Formato esperado pelo template

        # Receitas
        receita_categories = []
        receita_total = receitas_data.get('valor', 0)  # Valor total da categoria Receitas
        receita_subcategorias_sum = sum(subcat['valor'] for subcat in receitas_data.get('subcategorias', []))
        receita_restante = max(0, receita_total - receita_subcategorias_sum)  # Calcula o valor restante

        # Adiciona as 3 maiores subcategorias
        for subcat in receitas_data.get('subcategorias', []):
            receita_categories.append({
                "name": subcat['subcategoria'],
                "value": subcat['valor'],
                "representatividade": subcat['av'],
                "variacao": subcat['ah'],
                "barra_rep": round((subcat['valor'] / receita_total) * 100, 2) if receita_total != 0 else 0
            })

        # Adiciona "Outras categorias" se houver valor restante
        if receita_restante > 0:
            receita_categories.append({
                "name": "Outras categorias",
                "value": receita_restante,
                "representatividade": 0,  # Não temos AV para "Outras categorias"
                "variacao": 0,  # Não temos AH para "Outras categorias"
                "barra_rep": round((receita_restante / receita_total) * 100, 2) if receita_total != 0 else 0
            })

        # Custos Variáveis
        custo_categories = []
        custos_total = custos_data.get('valor', 0)  # Valor total da categoria Custos Variáveis
        custos_subcategorias_sum = sum(abs(subcat['valor']) for subcat in custos_data.get('subcategorias', []))
        custos_restante = max(0, abs(custos_total) - custos_subcategorias_sum)  # Calcula o valor restante

        # Adiciona as 3 maiores subcategorias
        for subcat in custos_data.get('subcategorias', []):
            custo_categories.append({
                "name": subcat['subcategoria'],
                "value": abs(subcat['valor']),  # Valor absoluto para exibição
                "representatividade": abs(subcat['av']),
                "variacao": subcat['ah'],
                "barra_rep": round((abs(subcat['valor']) / abs(custos_total)) * 100, 2) if custos_total != 0 else 0
            })

        # Adiciona "Outras categorias" se houver valor restante
        if custos_restante > 0:
            custo_categories.append({
                "name": "Outras categorias",
                "value": custos_restante,
                "representatividade": 0,  # Não temos AV para "Outras categorias"
                "variacao": 0,  # Não temos AH para "Outras categorias"
                "barra_rep": round((custos_restante / abs(custos_total)) * 100, 2) if custos_total != 0 else 0
            })

        # Dados para o template
        template_data = {
            "nome": cliente_nome,
            "Periodo": f"{mes_nome}/{ano}",
            "notas": notas,
            "receita": receitas_data.get('valor', 0),
            "represent_receita": 100.0,  # Receita sempre representa 100%
            "receita_categories": receita_categories,
            "custos": abs(custos_data.get('valor') or 0),  # Valor absoluto garantindo que None seja tratado como 0
            "represent_custos": abs(custos_data.get('valor') or 0) / (receitas_data.get('valor') or 1) * 100 if (receitas_data.get('valor') or 0) > 0 else 0,
            "custo_categories": custo_categories
        }
        
        # Renderizar template
        template = self.env.from_string(self._get_template_html())
        return template.render(
            data=template_data,
            logo_svg=logo_svg,
            seta_b64=seta_up_verde_b64,
            seta_b64_2=seta_down_laranja_b64,
            seta_b64_3=seta_up_laranja_b64,
            seta_b64_4=seta_down_verde_b64,
            cliente_nome=cliente_nome,
            mes_nome=mes_nome,
            ano=ano
        )
    
    def _get_template_html(self):
        """Retorna o template HTML para o relatório."""
        return '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Financeiro - {{ cliente_nome }} - {{ mes_nome }}/{{ ano }}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        /* Definir altura da página A4 (297mm) menos margens (5mm topo + 4mm base = 9mm) */
        
        /* Resetar margens e definir layout base */
        html, body {
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            position: relative;
            min-height: 100%; /* Garante que o body ocupe a página inteira */
        }

        /* Contêiner principal para o conteúdo */
        .main-content {
            padding: 20px 20px 5px 20px; /* Aumenta padding-bottom para reservar espaço para o footer */
            box-sizing: border-box;
            position: relative;
        }

        .section-title {
            font-size: 25px;
            font-weight: bold;
            margin-top: 6px;
            margin-bottom: 40px;
        }

        .notes-title {
            font-size: 18px;
            font-weight: 600;
            margin: 15px 0 8px 0;
            text-align: left;
            page-break-before: avoid;
        }

        .notes-title + .box-frame {
            margin-top: 8px;
            margin-bottom: 50px; /* Espaço suficiente para o footer */
            padding: 15px;
            page-break-inside: avoid;
            break-inside: avoid;
        }

        .bar-container {
            width: 100%;
            height: 28px;
            border-radius: 8px;
            overflow: hidden;
            margin: 2px 0 0 0;
        }

        .bar-segment {
            float: left;
            height: 100%;
        }

        .bar-total {
            font-size: 17px;
            text-align: right;
            margin-top: 5px;
        }

        .value {
            font-size: 25px;
            margin-top: -30px;
            margin-bottom: 40px;
            font-weight: 580;
        }

        hr.section-separator {
            border: none;
            border-top: 1px solid #ddd;
            margin: 20px 0;
        }

        .report-name, .report-period {
            color: #A5A5A5;
        }

        table.cat-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            border: none;
        }

        table.cat-table th, table.cat-table td {
            border: none;
            padding: 8px;
            text-align: left;
            background-color: #fff;
            font-family: 'Inter', sans-serif;
            font-weight: 200;
            font-size: 17px;
        }

        table.cat-table td:nth-child(3) {
            font-weight: 700;
        }

        table.cat-table td:nth-child(4), table.cat-table td:nth-child(5) {
            font-size: 14px;
        }

        table.cat-table thead {
            display: table-header-group;
        }

        table.cat-table thead th {
            visibility: hidden;
        }

        table.cat-table thead th:nth-child(4),
        table.cat-table thead th:nth-child(5) {
            visibility: visible;
            text-align: left;
            font-size: 14px;
            font-weight: 600;
        }

        .legend-box {
            width: 12px;
            height: 12px;
            border-radius: 2px;
        }

        .var-up img, .var-down img {
            vertical-align: middle;
            width: 10px;
            height: 7px;
            margin-right: 3px;
        }

        footer {
            position: fixed;
            bottom: 3mm; /* Ajustado para ficar dentro da margem de 4mm */
            left: 10mm;
            right: 10mm;
            width: calc(100% - 20mm);
            text-align: center;
            z-index: 9999; /* Aumentado para garantir que fique acima de tudo */
            height: 20px; /* Aumentado para melhor visibilidade */
        }

        footer img {
            height: 20px; /* Aumentado para melhor visibilidade, mas ainda dentro da margem */
            max-width: 100%;
            display: block; /* Garante que a imagem não cause espaçamentos indesejados */
            margin: 0 auto;
        }

        .header-accent {
            width: 100px;
            height: 6px;
            background-color: #FF6900;
            margin: 0 0 4px 40px;
            border-radius: 3px 3px 0 0;
        }

        .report-header {
            border-top: 1px solid #D9D9D9;
            margin: 0 0 8px 0;
        }

        .report-header-info {
            display: flex;
            justify-content: flex-start;
            align-items: center;
            width: 100%;
            font-size: 14px;
            margin: 4px 0 16px;
            white-space: nowrap;
        }

        .report-header-info .report-period {
            margin-left: auto;
        }

        .box-frame {
            page-break-inside: avoid;
            border: 1px solid #D9D9D9;
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 18px;
            margin-top: 30px;
        }

        .box-frame.blank {
            height: 100px;
            margin: 0 0 24px 0;
        }

        .notes-content {
            white-space: pre-wrap;
            text-align: left;
            margin: 0;
            padding: 0;
            font-size: 16px;
            line-height: 1.4;
        }
    </style>
    </head>
<body>
<div class="main-content">
  <!-- barra laranja acima da linha -->
  <div class="header-accent"></div>
  <div class="report-header"></div>
  <table style="width:100%; border-collapse:collapse; margin:4px 0 16px;">
    <tr>
        <td class="report-name" style="padding:0; text-align:left;  font-size:14px;">
            {{ data.nome }}
        </td>
        <td class="report-period" style="padding:0; text-align:right; font-size:14px;">
            {{ data.Periodo }}
        </td>
    </tr>
  </table>
  <div class="box-frame">
<div class="section">
    <div class="section-title">Receitas</div>
        {% set rec_colors = ['#007F4F', '#33B283', '#7FCEB1', '#ebebeb'] %}  <!-- Adiciona cor cinza para "Outras categorias" -->
        <div class="bar-container">
        {% for cat in data.receita_categories %}
            <div class="bar-segment"
                style="width: {{ cat.barra_rep }}%; background-color: {{ rec_colors[loop.index0 % rec_colors|length] }};">
            </div>
        {% endfor %}
        </div>
        <div class="bar-total">
        {{ '%.0f'|format(data.represent_receita) }}%
        </div>
        <div class="value">{{ data.receita|format_currency }}</div>
        <table class="cat-table">
            <colgroup>
                <col style="width:5%" />
                <col style="width:35%" />
                <col style="width:30%" />
                <col style="width:15%" />
                <col style="width:15%" />
            </colgroup>
            <thead>
                <tr>
                <th></th>
                <th>Categoria</th>
                <th>Valor</th>
                <th>AV</th>
                <th>AH</th>
                </tr>
            </thead>
            <tbody>
            {% for cat in data.receita_categories %}
            <tr>
                <td><div class="legend-box" style="background-color:{{ rec_colors[loop.index0 % rec_colors|length] }};"></div></td>
                <td>{{ cat.name }}</td>
                <td>{{ cat.value|format_currency }}</td>
                <td>
                    {% if cat.name == "Outras categorias" %}
                        -
                    {% else %}
                        {{ cat.representatividade|format_percentage }}
                    {% endif %}
                </td>
                <td>
                    {% if cat.name == "Outras categorias" %}
                        -
                    {% else %}
                        {% if cat.variacao >= 0 %}
                            <span class="var-up"> 
                            <img src="data:image/svg+xml;base64,{{ seta_b64 }}" alt="↑"/>
                            {{ cat.variacao|format_percentage }}
                            </span>
                        {% else %}
                            <span class="var-down">
                            <img src="data:image/svg+xml;base64,{{ seta_b64_2 }}" alt="↓"/>
                            {{ cat.variacao|format_percentage }}
                            </span>
                        {% endif %}
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
            </tbody>
        </table>
    </div>
    <hr class="section-separator"/>
    <div class="section">
    <div class="section-title">Custos Variáveis</div>
        {% set cost_colors = ['#E75F00', '#FF8733', '#FFB37F', '#ebebeb'] %}  <!-- Adiciona cor cinza para "Outras categorias" -->
        <div class="bar-container">
        {% for cat in data.custo_categories %}
            <div class="bar-segment"
                style="width: {{ cat.barra_rep }}%; background-color: {{ cost_colors[loop.index0 % cost_colors|length] }};">
            </div>
        {% endfor %}
        </div>
        <div class="bar-total">
        {{ '%.0f'|format(data.represent_custos) }}%
        </div>
        <div class="value">{{ data.custos|format_currency }}</div>
        <table class="cat-table">
            <colgroup>
                <col style="width:5%" />
                <col style="width:35%" />
                <col style="width:30%" />
                <col style="width:15%" />
                <col style="width:15%" />
            </colgroup>
            <thead>
                <tr>
                <th></th>
                <th>Categoria</th>
                <th>Valor</th>
                <th>AV</th>
                <th>AH</th>
                </tr>
            </thead>
            <tbody>
            {% for cat in data.custo_categories %}
            <tr>
                <td><div class="legend-box" style="background-color:{{ cost_colors[loop.index0 % cost_colors|length] }};"></div></td>
                <td>{{ cat.name }}</td>
                <td>{{ cat.value|format_currency }}</td>
                <td>
                    {% if cat.name == "Outras categorias" %}
                        -
                    {% else %}
                        {{ cat.representatividade|format_percentage }}
                    {% endif %}
                </td>
                <td>
                    {% if cat.name == "Outras categorias" %}
                        -
                    {% else %}
                        {% if cat.variacao >= 0 %}
                            <span class="var-up"> 
                            <img src="data:image/svg+xml;base64,{{ seta_b64_3 }}" alt="↑"/>
                            {{ cat.variacao|format_percentage }}
                            </span>
                        {% else %}
                            <span class="var-down">
                            <img src="data:image/svg+xml;base64,{{ seta_b64_4 }}" alt="↓"/>
                            {{ cat.variacao|format_percentage }}
                            </span>
                        {% endif %}
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
            </tbody>
        </table>
    </div>
  </div>
  <div class="notes-title">Notas</div>
  <div class="box-frame">
    <div class="notes-content">{{ data.notas }}</div>
  </div>
  </div>
  <footer>
    {{ logo_svg | safe }}
  </footer>
</body>
</html>
'''