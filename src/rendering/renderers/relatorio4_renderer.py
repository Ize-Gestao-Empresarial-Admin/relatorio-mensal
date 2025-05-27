# src/rendering/renderers/relatorio4_renderer.py
from typing import Dict, Any, List, Tuple, Union
from src.rendering.renderers.base_renderer import BaseRenderer
import os
import base64

class Relatorio4Renderer(BaseRenderer):
    """
    Renderizador para o Relatório 4 - Análise do Fluxo de Caixa 4
    Converte os dados do relatório em HTML para posterior geração de PDF.
    """
    
    def render(self, data: Union[List[Dict[str, Any]], Tuple[List[Dict[str, Any]], Dict[str, str]]], 
               cliente_nome: str, mes_nome: str, ano: int) -> str:
        """
        Renderiza os dados do Relatório 4 em HTML.

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
        # Estrutura: [{'categoria': 'Lucro Líquido', 'valor': X, 'subcategorias': [...]}, {'categoria': 'Resultados Não Operacionais', ...}]
        lucro_liquido_data = next((item for item in relatorio_data if item['categoria'] == 'Lucro Líquido'), {})
        resultados_nao_operacionais_data = next((item for item in relatorio_data if item['categoria'] == 'Resultados Não Operacionais'), {})

        # Formato esperado pelo template

        # Lucro Líquido
        lucro_liquido_categories = []
        lucro_liquido_total = lucro_liquido_data.get('valor', 0)  # Valor total da categoria Lucro Líquido
        lucro_liquido_subcategorias_sum = sum(abs(subcat['valor']) for subcat in lucro_liquido_data.get('subcategorias', []))
        lucro_liquido_restante = max(0, abs(lucro_liquido_total) - lucro_liquido_subcategorias_sum)  # Calcula o valor restante
        


        # Adiciona as 3 maiores subcategorias
        for subcat in lucro_liquido_data.get('subcategorias', []):
            lucro_liquido_categories.append({
                "name": subcat['subcategoria'],
                "value": abs(subcat['valor']),
                "representatividade": subcat['av'],
                "variacao": subcat['ah'],
                "barra_rep": subcat['representatividade']
            })

        # Resultados Não Operacionais
        resultados_nao_operacionais_categories = []
        resultados_nao_operacionais_total = resultados_nao_operacionais_data.get('valor', 0)  # Valor total da categoria Resultados Não Operacionais
        resultados_nao_operacionais_subcategorias_sum = sum(abs(subcat['valor']) for subcat in resultados_nao_operacionais_data.get('subcategorias', []))
        resultados_nao_operacionais_restante = max(0, abs(resultados_nao_operacionais_total) - resultados_nao_operacionais_subcategorias_sum)  # Calcula o valor restante
        
        #receita chamada pra realização de operações
        receita_total = next((subcat['valor'] for subcat in lucro_liquido_data.get('subcategorias', []) if subcat['subcategoria'] == 'Receita'), 0)     
        
        # Adiciona as 3 maiores subcategorias
        for subcat in resultados_nao_operacionais_data.get('subcategorias', []):
            resultados_nao_operacionais_categories.append({
                "name": subcat['subcategoria'],
                "value": subcat['valor'],  # Valor absoluto para exibição
                "representatividade": abs(subcat['av']),
                "variacao": subcat['ah'],
                "barra_rep": subcat['representatividade']  # Usar o valor corrigido diretamente
            })

        # Adiciona "Outras categorias" se houver valor restante
        if resultados_nao_operacionais_restante > 0:
            resultados_nao_operacionais_categories.append({
                "name": "Outras categorias",
                "value": resultados_nao_operacionais_restante,
                "representatividade": 0,  # Não temos AV para "Outras categorias"
                "variacao": 0,  # Não temos AH para "Outras categorias"
                "barra_rep": round((resultados_nao_operacionais_restante / abs(resultados_nao_operacionais_total)) * 100, 2) if resultados_nao_operacionais_total != 0 else 0
            })

        # Dados para o template
        template_data = {
            "nome": cliente_nome,
            "Periodo": f"{mes_nome}/{ano}",
            "notas": notas,
            "lucro_liquido": lucro_liquido_data.get('valor', 0),
            "represent_lucro_liquido": round((lucro_liquido_total / receita_total) * 100, 2) if receita_total != 0 else 0, 
            "lucro_liquido_categories": lucro_liquido_categories,
            "resultados_nao_operacionais": resultados_nao_operacionais_data.get('valor') or 0,  # Valor absoluto garantindo que None seja tratado como 0
            "represent_resultados_nao_operacionais": round((resultados_nao_operacionais_total / receita_total) * 100, 2) if receita_total != 0 else 0,
            "resultados_nao_operacionais_categories": resultados_nao_operacionais_categories
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
            padding: 20px 20px 140px 20px; /* Uniforme, conforme sua correção */
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
        
        .fixed-footer-bg {
            position: fixed;           /* sai do fluxo normal */
            bottom: -130px;                 /* gruda na base da página */
            left: 45%;                 /* centraliza horizontalmente */
            transform: translateX(-50%);
            z-index: -1;               /* garante que fique atrás de tudo */
            width: 80px;              /* ajuste à largura que desejar */
            height: auto;
            /* opacity: 1;           — opcional, se quiser “esmaecer” um pouco */
        }
    </style>
</head>
<body>
    
    <div class="main-content">
    <img src="data:image/png;base64,{{ logo_svg }}" class="fixed-footer-bg" alt=""/>
        <!-- barra laranja acima da linha -->
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
                <div class="section-title">Lucro Líquido</div>
                {% set lucro_colors = ['#007F4F', '#33B283', '#7FCEB1', '#CCECE0'] %}
                <div class="bar-container">
                {% for cat in data.lucro_liquido_categories %}
                    <div class="bar-segment"
                        style="width: {{ cat.barra_rep }}%; background-color: {{ lucro_colors[loop.index0 % lucro_colors|length] }};">
                    </div>
                {% endfor %}
                </div>
                <div class="bar-total">
                {{ '%.0f'|format(data.represent_lucro_liquido) }}%
                </div>
                <div class="value">{{ data.lucro_liquido|format_currency }}</div>
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
                    {% for cat in data.lucro_liquido_categories %}
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
                <div class="section-title">Resultados Não Operacionais</div>
                {% set resultados_colors = ['#E75F00', '#FF8733', '#FFB37F', '#ebebeb'] %}
                <div class="bar-container">
                {% for cat in data.resultados_nao_operacionais_categories %}
                    <div class="bar-segment"
                        style="width: {{ cat.barra_rep }}%; background-color: {{ resultados_colors[loop.index0 % resultados_colors|length] }};">
                    </div>
                {% endfor %}
                </div>
                <div class="bar-total">
                {{ '%.0f'|format(data.represent_resultados_nao_operacionais) }}%
                </div>
                <div class="value">{{ data.resultados_nao_operacionais|format_currency }}</div>
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
                    {% for cat in data.resultados_nao_operacionais_categories %}
                    <tr>
                        <td><div class="legend-box" style="background-color:{{ resultados_colors[loop.index0 % resultados_colors|length] }};"></div></td>
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

</body>
</html>
'''