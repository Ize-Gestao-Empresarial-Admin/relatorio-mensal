from typing import Dict, Any, List, Tuple, Union
from src.rendering.renderers.base_renderer import BaseRenderer
import os
import base64

class Relatorio3Renderer(BaseRenderer):
    """
    Renderizador para o Relatório 3 - Análise de Lucro Operacional e Investimentos.
    Converte os dados do relatório em HTML para posterior geração de PDF.
    """
    
    def render(self, data: Union[List[Dict[str, Any]], Tuple[List[Dict[str, Any]], Dict[str, str]]], 
               cliente_nome: str, mes_nome: str, ano: int) -> str:
        """
        Renderiza os dados do Relatório 3 em HTML.
        
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
        lucro_operacional_data = next((item for item in relatorio_data if item['categoria'] == 'Lucro Operacional'), {})
        
        investimentos_data = next((item for item in relatorio_data if item['categoria'] == 'Investimentos'), {})

        #receita chamada pra realização de operações
        receita_total = next((subcat['valor'] for subcat in lucro_operacional_data.get('subcategorias', []) if subcat['subcategoria'] == 'Receita'), 0) 
        
        # Lucro Operacional
        lucro_operacional_categories = []
        lucro_operacional_total = lucro_operacional_data.get('valor', 0)
        lucro_operacional_subcategorias_sum = sum(subcat['valor'] for subcat in lucro_operacional_data.get('subcategorias', []))
        lucro_operacional_restante = max(0,lucro_operacional_total - lucro_operacional_subcategorias_sum)  # Calcula o valor restante

        for subcat in lucro_operacional_data.get('subcategorias', []):
            lucro_operacional_categories.append({
                "name": subcat['subcategoria'],
                "value": abs(subcat['valor']),  # Valor absoluto para exibição
                "representatividade": abs(subcat['av']),
                "variacao": subcat['ah'],
                "barra_rep": subcat['representatividade'] 
            })
        
        # Adiciona "Outras categorias" se houver valor restante
        if lucro_operacional_restante > 0:
            lucro_operacional_categories.append({
                "name": "Outras categorias",
                "value": lucro_operacional_restante,
                "representatividade": 0,  # Não temos AV para "Outras categorias"
                "variacao": 0,  # Não temos AH para "Outras categorias"
                "barra_rep": round((lucro_operacional_restante / lucro_operacional_total) * 100, 2) if lucro_operacional_total != 0 else 0
            })

        # Investimentos
        investimentos_categories = []
        investimentos_total = investimentos_data.get('valor', 0) 
        investimentos_subcategorias_sum = sum(abs(subcat['valor']) for subcat in investimentos_data.get('subcategorias', []))
        investimentos_restante = max(0, abs(investimentos_total) - investimentos_subcategorias_sum)  # Calcula o valor restante
        investimentos_av = investimentos_data.get('av_categoria', 0)  # AV da categoria Lucro Bruto

        for subcat in investimentos_data.get('subcategorias', []):
            investimentos_categories.append({
                "name": subcat['subcategoria'],
                "value": subcat['valor'],  # Valor absoluto para exibição
                "representatividade": abs(subcat['av']), #nesse caso em especifico esta usando o AV
                "variacao": subcat['ah'],
                "barra_rep": round((abs(subcat['valor']) / abs(investimentos_total)) * 100, 2) if investimentos_total != 0 else 0
            })

        # Adiciona "Outras categorias" se houver valor restante
        if investimentos_restante > 0:
            investimentos_categories.append({
                "name": "Outras categorias",
                "value": investimentos_restante,
                "representatividade": 0,  # Não temos AV para "Outras categorias"
                "variacao": 0,  # Não temos AH para "Outras categorias"
                "barra_rep": round((investimentos_restante / abs(investimentos_total)) * 100, 2) if investimentos_total != 0 else 0
            })


        # Dados para o template
        template_data = {
            "nome": cliente_nome,
            "Periodo": f"{mes_nome}/{ano}",
            "notas": notas,
            "lucro_operacional": lucro_operacional_total,
            "represent_lucro_operacional": round((lucro_operacional_total / receita_total) * 100, 2) if receita_total != 0 else 0,
            "lucro_operacional_categories": lucro_operacional_categories,
            "investimentos": abs(investimentos_total),
            "represent_investimentos": abs(investimentos_av) or 0,  # AV absoluto garantindo que None seja tratado como 0
            "investimentos_categories": investimentos_categories
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
            padding: 20px 20px 90px 20px; /* Uniforme, conforme correção */
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
                <div class="section-title">Lucro Operacional</div>
                {% set lucro_colors = ['#007F4F', '#33B283', '#7FCEB1', '#ebebeb'] %}
                <div class="bar-container">
                {% for cat in data.lucro_operacional_categories %}
                    <div class="bar-segment"
                        style="width: {{ cat.barra_rep }}%; background-color: {{ lucro_colors[loop.index0 % lucro_colors|length] }};">
                    </div>
                {% endfor %}
                </div>
                <div class="bar-total">
                {{ '%.0f'|format(data.represent_lucro_operacional) }}%
                </div>
                <div class="value">{{ data.lucro_operacional|format_currency }}</div>
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
                    {% for cat in data.lucro_operacional_categories %}
                    <tr>
                        <td><div class="legend-box" style="background-color:{{ lucro_colors[loop.index0 % lucro_colors|length] }};"></div></td>
                        <td>{{ cat.name }}</td>
                        <td>{{ cat.value|format_currency }}</td>
                        <td>{{ cat.representatividade|format_percentage }}</td>
                        <td>
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
                        </td>
                    </tr>
                    {% endfor %}
                    </tbody>
                </table>
            </div>
            <hr class="section-separator"/>
            <div class="section">
                <div class="section-title">Investimentos</div>
                {% set invest_colors = ['#E75F00', '#FF8733', '#FFB37F', '#ebebeb'] %}
                <div class="bar-container">
                {% for cat in data.investimentos_categories %}
                    <div class="bar-segment"
                        style="width: {{ cat.barra_rep }}%; background-color: {{ invest_colors[loop.index0 % invest_colors|length] }};">
                    </div>
                {% endfor %}
                </div>
                <div class="bar-total">
                {{ '%.0f'|format(data.represent_investimentos) }}%
                </div>
                <div class="value">{{ data.investimentos|format_currency }}</div>
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
                    {% for cat in data.investimentos_categories %}
                    <tr>
                        <td><div class="legend-box" style="background-color:{{ invest_colors[loop.index0 % invest_colors|length] }};"></div></td>
                        <td>{{ cat.name }}</td>
                        <td>{{ cat.value|format_currency }}</td>
                        <td>{{ cat.representatividade|format_percentage }}</td>
                        <td>
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