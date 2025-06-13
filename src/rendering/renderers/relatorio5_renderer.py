from typing import Dict, Any, List, Tuple, Union
from src.rendering.renderers.base_renderer import BaseRenderer
import os
import base64
import logging
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
import io
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import LinearSegmentedColormap

logger = logging.getLogger(__name__)

class Relatorio5Renderer(BaseRenderer):
    """Renderizador específico para o Relatório 5 - Geração de Caixa"""
    
    def __init__(self):
        super().__init__()
        # Carregar o template do relatório 5
        self.template = self.env.get_template("relatorio5/template.html")
    
    def generate_histogram_base64(self, analise_temporal_data, config=None):
        """Gera o gráfico de histograma usando dados reais da análise temporal"""
        # Configurações padrão
        default_config = {
            'bar_width': 0.09,
            'figure_size': (10, 6),
            'dpi': 800,
            'line_width': 1.9,
            'marker_size': 80,
            'colors': {
                'positive': '#007F4F',
                'negative': '#E75F00',
                'accumulated': '#B1B1B1',
                'accumulated_points': '#000000',
                'mean_line': "#6A6969",
                'gradient_start': '#B1B1B1',
                'gradient_end': '#F5F5F5'
            },
            'margins': {
                'top': 1.2,
                'bottom': 1.0
            },
            'annotations': {
                'show_bar_values': True,
                'show_acc_values': True,
                'show_mean_label': True,
                'font_size_bars': 10,
                'font_size_acc': 10,
                'font_size_mean': 10,
                'show_legend': True,
                'font_size_legend': 9
            },
            'styling': {
                'bar_edge_width': 8,
                'marker_edge_width': 2,
                'mean_line_style': '--',
                'mean_line_width': 1.5,
                'spine_color': '#69696F',
                'spine_width': 0.5,
                'gradient_alpha_start': 0.4,
                'gradient_alpha_end': 0.0
            },
            'bar_radius': 0.5
        }
        
        # Mesclar configurações personalizadas
        if config:
            for key, value in config.items():
                if isinstance(value, dict) and key in default_config:
                    default_config[key].update(value)
                else:
                    default_config[key] = value
        
        cfg = default_config
        
        # Extrair dados reais da análise temporal
        meses_data = analise_temporal_data.get('meses', [])
        if not meses_data:
            logger.warning("Nenhum dado de análise temporal encontrado")
            return ""
        
        # CORREÇÃO: Inverter a ordem dos dados para mostrar cronologicamente
        meses_data_ordenados = sorted(meses_data, key=lambda x: x['mes'])
        
        # Preparar dados para o gráfico na ordem cronológica correta
        meses = []
        geracao_caixa = []
        
        for item in meses_data_ordenados:
            # Converter formato "YYYY-MM" para nome do mês
            ano_mes = item['mes']
            ano, mes = ano_mes.split('-')
            
            # Mapear número do mês para nome abreviado
            nomes_meses = {
                '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr',
                '05': 'Mai', '06': 'Jun', '07': 'Jul', '08': 'Ago',
                '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
            }
            
            nome_mes = f"{nomes_meses[mes]}/{ano[-2:]}"  # Ex: "Mar/25"
            meses.append(nome_mes)
            geracao_caixa.append(item['valor'])
        
        media = analise_temporal_data.get('media', 0)
        
        # Calcular valores acumulados na ordem cronológica
        acumulado = np.cumsum(geracao_caixa)
        
        # NOVO: Criar valores absolutos para posicionamento da linha
        acumulado_absoluto = np.abs(acumulado)
        
        # Definir cores baseadas nos valores
        cores = [cfg['colors']['positive'] if valor >= 0 else cfg['colors']['negative'] 
                 for valor in geracao_caixa]
        
        # Configurações do gráfico
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=cfg['figure_size'], dpi=cfg['dpi'])
        
        # Função para formatação de valores no eixo Y - ALTERADA: formato abreviado
        def y_fmt(value, tick_number):
            abs_val = abs(value)
            if abs_val >= 1_000_000:
                return f"{value/1_000_000:.0f}M"
            elif abs_val >= 1_000:
                return f"{value/1_000:.0f}k"
            else:
                return f"{value:.0f}"
        
        # Criar barras (todas começam do 0)
        barras = []
        for i, (val, cor) in enumerate(zip(geracao_caixa, cores)):
            altura_barra = abs(val)
            
            rect = Rectangle(
                (i - cfg['bar_width']/2, 0), 
                cfg['bar_width'], altura_barra,
                facecolor=cor, 
                edgecolor=cor,
                linewidth=cfg['styling']['bar_edge_width'],
                joinstyle='round',
                zorder=3
            )
            ax.add_patch(rect)
            barras.append(rect)
        
        # Adicionar valores nas barras
        if cfg['annotations']['show_bar_values']:
            for i, height in enumerate(geracao_caixa):
                y_position = abs(height) * 0.05
                valor_formatado = f"R${height:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                
                ax.annotate(valor_formatado,
                            xy=(i, y_position),
                            ha='center', va='bottom',
                            fontsize=cfg['annotations']['font_size_bars'], 
                            fontweight='bold',
                            color='black',
                            rotation=90)
        
        # Criar linha de acumulado suavizada - MODIFICADO: usar valores absolutos para posicionamento
        x = np.array(range(len(meses)))
        y = np.array(acumulado_absoluto)  # ALTERADO: usar valores absolutos
        y_real = np.array(acumulado)      # NOVO: manter valores reais para os rótulos
        
        if len(meses) > 2:
            x_smooth = np.linspace(x.min(), x.max(), 300)
            k = min(2, len(meses)-1)
            spl = make_interp_spline(x, y, k=k)  # usar valores absolutos para a curva
            y_smooth = spl(x_smooth)
            
            # Criar degradê linear
            from matplotlib.colors import to_rgb
            cor_cinza = to_rgb(cfg['colors']['gradient_start'])
            
            colors = [
                (*cor_cinza, cfg['styling']['gradient_alpha_end']),
                (*cor_cinza, cfg['styling']['gradient_alpha_start'])
            ]
            
            cmap = LinearSegmentedColormap.from_list('gradient_cinza', colors, N=256)
            
            y_min = 0
            y_max = np.max(y_smooth)
            
            X, Y = np.meshgrid(x_smooth, np.linspace(y_min, y_max, 256))
            Z = np.zeros_like(Y)
            for i, x_val in enumerate(x_smooth):
                y_linha = y_smooth[i]
                mask = Y[:, i] <= y_linha
                Z[:, i] = Y[:, i] / y_max
                Z[~mask, i] = np.nan
            
            ax.imshow(Z, extent=[x_smooth.min(), x_smooth.max(), y_min, y_max], 
                      aspect='auto', origin='lower', cmap=cmap, 
                      alpha=1.0, zorder=1, interpolation='bilinear')
            
            line = ax.plot(x_smooth, y_smooth, 
                          color=cfg['colors']['accumulated'], 
                          linewidth=cfg['line_width'], 
                          zorder=4)
        else:
            # Para poucos pontos, usar degradê simples
            from matplotlib.colors import to_rgb
            cor_cinza = to_rgb(cfg['colors']['gradient_start'])
            
            ax.fill_between(x, 0, y, 
                           color=cor_cinza,
                           alpha=cfg['styling']['gradient_alpha_start'],
                           zorder=1)
            
            line = ax.plot(x, y, 
                          color=cfg['colors']['accumulated'], 
                          linewidth=cfg['line_width'], 
                          zorder=4)
        
        # Adicionar pontos de acumulado - MODIFICADO: usar posições absolutas
        scatter = ax.scatter(x, y, 
                            s=cfg['marker_size'], 
                            color=cfg['colors']['accumulated_points'],
                            edgecolor='white', 
                            linewidth=cfg['styling']['marker_edge_width'], 
                            zorder=5)
        
        # Adicionar valores de acumulado - MODIFICADO: z-order alto para sobrepor qualquer elemento
        if cfg['annotations']['show_acc_values']:
            for i, (valor_real, valor_abs) in enumerate(zip(acumulado, acumulado_absoluto)):
                # ALTERADO: formatar o valor real (com sinal), mas posicionar no valor absoluto
                valor_formatado = f"R${valor_real:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                
                ax.annotate(valor_formatado, 
                           (i, valor_abs),  # ALTERADO: posicionar no valor absoluto
                           textcoords="offset points", 
                           xytext=(0,15), 
                           ha='center', 
                           fontsize=cfg['annotations']['font_size_acc'],
                           fontweight='bold',
                           color='#4A4A4A',
                           zorder=20)  # ALTERADO: z-order muito alto (20) para sobrepor tudo, sem bbox
        
        # Linha de média tracejada - MODIFICADO: sempre mostrar, usar valor absoluto para posicionamento
        if media != 0:  # ALTERADO: mostrar sempre que não for zero
            media_absoluta = abs(media)  # NOVO: usar valor absoluto para posicionamento
            
            mean_line = ax.axhline(media_absoluta,  # ALTERADO: posicionar no valor absoluto
                                  color=cfg['colors']['mean_line'],
                                  linestyle=cfg['styling']['mean_line_style'], 
                                  linewidth=cfg['styling']['mean_line_width'], 
                                  zorder=2,
                                  label='Média dos últimos 3 meses')
            
            if cfg['annotations']['show_mean_label']:
                # ALTERADO: formatar com valor real (com sinal), mas posicionar no absoluto
                media_formatada = f"R${media:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                posicao_x_media = len(meses) - 1 + 0.35
                
                ax.annotate(media_formatada, 
                            (posicao_x_media, media_absoluta),  # ALTERADO: posicionar no valor absoluto
                            textcoords="offset points",
                            xytext=(0, 2),
                            ha='left',
                            va='bottom',
                            fontsize=cfg['annotations']['font_size_mean'],
                            fontweight='bold',
                            color=cfg['colors']['mean_line'])
        
        # Adicionar legenda - MODIFICADO: sempre mostrar quando houver média
        if cfg['annotations']['show_legend'] and media != 0:  # ALTERADO: condição mudada
            legend = ax.legend(loc='upper right',
                              fontsize=cfg['annotations']['font_size_legend'],
                              frameon=False,
                              handlelength=2.0,
                              handletextpad=0.8)
            
            for text in legend.get_texts():
                text.set_color('#2D2B3A')
                text.set_fontweight('normal')
        
        # Configurar eixos - MODIFICADO: considerar média absoluta no y_max
        ax.set_xlim(-0.5, len(meses) - 1 + 0.8)
        
        y_max_barras = max([abs(val) for val in geracao_caixa]) if geracao_caixa else 0
        y_max_acumulado = max(acumulado_absoluto) if len(acumulado_absoluto) > 0 else 0
        y_max_media = abs(media) if media != 0 else 0  # NOVO: considerar média absoluta
        y_max = max(y_max_barras, y_max_acumulado, y_max_media) * cfg['margins']['top']  # ALTERADO
        
        ax.set_ylim(0, y_max)  # Sempre começar do 0
        
        # Estilizar gráfico
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        
        ax.spines["bottom"].set_color(cfg['styling']['spine_color'])
        ax.spines["left"].set_color(cfg['styling']['spine_color'])
        ax.spines["bottom"].set_linewidth(cfg['styling']['spine_width'])
        ax.spines["left"].set_linewidth(cfg['styling']['spine_width'])
        
        ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))
        ax.tick_params(axis='both', which='major', length=0, 
                      labelcolor=cfg['styling']['spine_color'], pad=12)
        
        ax.set_xticks(range(len(meses)))
        ax.set_xticklabels(meses)
        ax.set_axisbelow(True)
        ax.grid(False)
        
        plt.tight_layout()
        
        # Converter para base64
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=cfg['dpi'])
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def render(self, data: Union[List[Dict[str, Any]], Tuple[List[Dict[str, Any]], Dict[str, str]]], 
               cliente_nome: str, mes_nome: str, ano: int) -> str:
        """
        Renderiza os dados do Relatório 5 em HTML.

        Args:
            data: Lista de dados do relatório ou tupla com dados e notas.
            cliente_nome: Nome do cliente.
            mes_nome: Nome do mês.
            ano: Ano do relatório.

        Returns:
            HTML formatado.
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
        
        # Carregar rodapé
        rodape_path = os.path.join(icons_dir, "rodape.png")
        try:
            with open(rodape_path, "rb") as f:
                icon_bytes = f.read()
                logger.info(f"Arquivo rodapé lido com sucesso: {rodape_path}, tamanho: {len(icon_bytes)} bytes")
                icon_rodape = base64.b64encode(icon_bytes).decode("ascii")
                logger.info(f"Base64 do rodapé gerado com sucesso, tamanho: {len(icon_rodape)}")
        except Exception as e:
            logger.error(f"Erro ao carregar rodapé: {str(e)}")
            icon_rodape = ""
        
        # Setas (carregar como base64)
        seta_up_verde_path = os.path.join(icons_dir, "SETA-UP-VERDE.svg")
        with open(seta_up_verde_path, "rb") as f:
            seta_up_verde_b64 = base64.b64encode(f.read()).decode("utf-8")
        
        seta_down_laranja_path = os.path.join(icons_dir, "SETA-DOWN-LARANJA.svg")
        with open(seta_down_laranja_path, "rb") as f:
            seta_down_laranja_b64 = base64.b64encode(f.read()).decode("utf-8")
            
        # Processar dados do relatório
        geracao_de_caixa_data = next((item for item in relatorio_data if item['categoria'] == 'Geração de Caixa'), {})
        
        # Gerar gráfico de histograma usando dados reais
        histogram_base64 = ""
        analise_temporal = geracao_de_caixa_data.get('analise_temporal', {})
        if analise_temporal:
            try:
                histogram_base64 = self.generate_histogram_base64(analise_temporal)
                logger.info("Gráfico de histograma gerado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao gerar gráfico de histograma: {str(e)}")
                histogram_base64 = ""
        else:
            logger.warning("Dados de análise temporal não encontrados")
        
        # Geração de Caixa
        geracao_de_caixa_categories = []
        geracao_de_caixa_total = geracao_de_caixa_data.get('valor', 0)
        geracao_de_caixa_av = geracao_de_caixa_data.get('av_categoria', 0)
        
        for subcat in geracao_de_caixa_data.get('subcategorias', []):
            geracao_de_caixa_categories.append({
                "name": subcat['subcategoria'],
                "value": subcat['valor'],
                "representatividade": abs(subcat['av']),  # AV em relação à receita
                "variacao": subcat['ah'],
                "barra_rep": abs(subcat['barra_rep'])  # CORRIGIDO: usar barra_rep para largura das barras
            })

        # Dados para o template
        template_data = {
            "nome": cliente_nome,
            "Periodo": f"{mes_nome}/{ano}",
            "notas": notas,
            "geracao_de_caixa": geracao_de_caixa_total,
            "represent_geracao_de_caixa": abs(geracao_de_caixa_av) or 0,
            "geracao_de_caixa_categories": geracao_de_caixa_categories
        }
        
        # Renderizar o template
        return self.template.render(
            data=template_data,
            icon_rodape=icon_rodape,
            seta_b64=seta_up_verde_b64,
            seta_b64_2=seta_down_laranja_b64,
            histogram_base64=histogram_base64,  # NOVO: Adicionar gráfico
            cliente_nome=cliente_nome,
            mes_nome=mes_nome,
            ano=ano
        )