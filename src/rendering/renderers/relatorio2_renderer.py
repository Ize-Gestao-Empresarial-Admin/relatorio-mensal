# src/rendering/renderers/relatorio2_renderer.py
from typing import Dict, Any, List, Tuple, Union
from src.rendering.renderers.base_renderer import BaseRenderer
import os
import base64

class Relatorio2Renderer(BaseRenderer):
    """
    Renderizador para o Relatório 2 - Análise de Fluxo de Caixa 2.
    Converte os dados do relatório em HTML para posterior geração de PDF.
    """
    
    def render(self, data: Union[List[Dict[str, Any]], Tuple[List[Dict[str, Any]], Dict[str, str]]], 
               cliente_nome: str, mes_nome: str, ano: int) -> str:
        """
        Renderiza os dados do Relatório 2 em HTML.
        
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
        # Estrutura: [{'categoria': 'Lucro Bruto', 'valor': X, 'subcategorias': [...]}, {'categoria': 'Despesas Fixas', ...}]
        lucro_bruto_data = next((item for item in relatorio_data if item['categoria'] == 'Lucro Bruto'), {})
        despesas_fixas_data = next((item for item in relatorio_data if item['categoria'] == 'Despesas Fixas'), {})

        # Lucro Bruto
        lucro_bruto_categories = []
        lucro_bruto_total = lucro_bruto_data.get('valor', 0)  # Valor total da categoria Lucro Bruto
        lucro_bruto_av = lucro_bruto_data.get('av_categoria', 0)  # AV da categoria Lucro Bruto
        
        #receita chamada pra realização de operações
        receita_total = next((subcat['valor'] for subcat in lucro_bruto_data.get('subcategorias', []) if subcat['subcategoria'] == 'Receita'), 0) 
        
        # Calcular AV do Lucro Bruto
        subcats = lucro_bruto_data.get("subcategorias", [])
        av_receita = next((s["av"] for s in subcats if s["subcategoria"] == "Receita"), 0)
        av_custos_variaveis = next((s["av"] for s in subcats if s["subcategoria"] == "Custos Variáveis"), 0)
        av_lucro_bruto = av_receita - av_custos_variaveis


        # Adiciona as subcategorias
        for subcat in lucro_bruto_data.get('subcategorias', []):
            lucro_bruto_categories.append({
                "name": subcat['subcategoria'],
                "value": abs(subcat['valor']),
                "representatividade": subcat['av'],
                "variacao": subcat['ah'],
                "barra_rep": subcat['representatividade']
                    #round((subcat['valor'] / lucro_bruto_total) * 100, 2) if lucro_bruto_total != 0 else 0
            })


        # Despesas Fixas
        despesas_fixas_categories = []
        despesas_fixas_total = despesas_fixas_data.get('valor', 0)  # Valor total da categoria Despesas Fixas
        despesas_fixas_subcategorias_sum = sum(abs(subcat['valor']) for subcat in despesas_fixas_data.get('subcategorias', []))
        despesas_fixas_restante = max(0, abs(despesas_fixas_total) - despesas_fixas_subcategorias_sum)  # Calcula o valor restante
        despesas_fixas_av = despesas_fixas_data.get('av_categoria', 0)  # AV da categoria Lucro Bruto

        # Adiciona as subcategorias
        for subcat in despesas_fixas_data.get('subcategorias', []):
            despesas_fixas_categories.append({
                "name": subcat['subcategoria'],
                "value": abs(subcat['valor']),  # Valor absoluto para exibição
                "representatividade": abs(subcat['av']),
                "variacao": subcat['ah'],
                "barra_rep": round((abs(subcat['valor']) / abs(despesas_fixas_total)) * 100, 2) if despesas_fixas_total != 0 else 0
            })

        # Adiciona "Outras categorias" se houver valor restante
        if despesas_fixas_restante > 0:
            despesas_fixas_categories.append({
                "name": "Outras categorias",
                "value": despesas_fixas_restante,
                "representatividade": 0,  # Não temos AV para "Outras categorias"
                "variacao": 0,  # Não temos AH para "Outras categorias"
                "barra_rep": round((despesas_fixas_restante / abs(despesas_fixas_total)) * 100, 2) if despesas_fixas_total != 0 else 0
            })

        # Dados para o template
        template_data = {
            "nome": cliente_nome,
            "Periodo": f"{mes_nome}/{ano}",
            "notas": notas,
            "lucro_bruto": lucro_bruto_data.get('valor', 0),
            "represent_lucro_bruto": abs(lucro_bruto_av) or 0,
            "lucro_bruto_categories": lucro_bruto_categories,
            "despesas_fixas": abs(despesas_fixas_data.get('valor') or 0),  # Valor absoluto garantindo que None seja tratado como 0
            "represent_despesas_fixas": abs(despesas_fixas_av) or 0,  # AV absoluto garantindo que None seja tratado como 0
            "despesas_fixas_categories": despesas_fixas_categories
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
            padding: 20px 20px 80px 20px; /* Uniforme, conforme sua correção */
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
            margin-top: 2px;
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
            margin: 25px 0;
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
            bottom: 3mm; /* Dentro da margem inferior de 4mm */
            left: 10mm;
            right: 10mm;
            width: calc(100% - 20mm);
            text-align: center;
            z-index: 9999; /* Garante que fique acima de tudo */
            height: 20px; /* Altura ajustada */
        }

        footer img {
            height: 20px; /* Dentro da margem, visível */
            max-width: 100%;
            display: block;
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
        <div class="header-accent"></div>
        <div class="report-header"></div>
        <table style="width:100%; border-collapse:collapse; margin:4px 0 16px;">
            <tr>
                <td class="report-name" style="padding:0; text-align:left; font-size:14px;">
                    {{ data.nome }}
                </td>
                <td class="report-period" style="padding:0; text-align:right; font-size:14px;">
                    {{ data.Periodo }}
                </td>
            </tr>
        </table>
        <div class="box-frame">
            <div class="section">
                <div class="section-title">Lucro Bruto</div>
                {% set lucro_colors = ['#007F4F', '#33B283', '#7FCEB1', '#ebebeb'] %}
                <div class="bar-container">
                {% for cat in data.lucro_bruto_categories %}
                    <div class="bar-segment"
                        style="width: {{ cat.barra_rep }}%; background-color: {{ lucro_colors[loop.index0 % lucro_colors|length] }};">
                    </div>
                {% endfor %}
                </div>
                <div class="bar-total">
                {{ '%.0f'|format(data.represent_lucro_bruto) }}%
                </div>
                <div class="value">{{ data.lucro_bruto|format_currency }}</div>
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
                    {% for cat in data.lucro_bruto_categories %}
                    <tr>
                        <td><div class="legend-box" style="background-color:{{ lucro_colors[loop.index0 % lucro_colors|length] }};"></div></td>
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
                <div class="section-title">Despesas Fixas</div>
                {% set despesas_colors = ['#E75F00', '#FF8733', '#FFB37F', '#ebebeb'] %}
                <div class="bar-container">
                {% for cat in data.despesas_fixas_categories %}
                    <div class="bar-segment"
                        style="width: {{ cat.barra_rep }}%; background-color: {{ despesas_colors[loop.index0 % despesas_colors|length] }};">
                    </div>
                {% endfor %}
                </div>
                <div class="bar-total">
                {{ '%.0f'|format(data.represent_despesas_fixas) }}%
                </div>
                <div class="value">{{ data.despesas_fixas|format_currency }}</div>
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
                    {% for cat in data.despesas_fixas_categories %}
                    <tr>
                        <td><div class="legend-box" style="background-color:{{ despesas_colors[loop.index0 % despesas_colors|length] }};"></div></td>
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