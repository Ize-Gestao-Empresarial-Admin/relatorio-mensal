import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
import base64
import io
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

def generate_histogram_base64(config=None):
    # Configurações padrão adaptadas do estilo do relatorio6
    default_config = {
        'bar_width': 0.09,           # Largura das barras 
        'figure_size': (10, 6),      # Tamanho da figura (largura, altura)
        'dpi': 300,                  # Resolução
        'show_legend': False,        # Legenda no gráfico (você tem externa no HTML)
        'legend_position': 'upper right',  # Posição da legenda
        'line_width': 1.9,           # Espessura da linha de acumulado
        'marker_size': 80,           # Tamanho dos pontos
        'colors': {
            'positive': '#007F4F',      # Verde - geração positiva
            'negative': '#E75F00',      # Laranja - geração negativa
            'accumulated': '#B1B1B1',   # Cinza - linha acumulado
            'accumulated_points': '#000000',  # Preto - pontos do acumulado
            'mean_line': "#6A6969",     # Cinza - linha da média
            'text': '#2D2B3A',          # Texto principal
            'axis_text': '#69696F'      # Texto dos eixos
        },
        'margins': {
            'top': 1.2,     # Margem superior (multiplicador)
            'bottom': 1.0   # Margem inferior (agora será 0)
        },
        'annotations': {
            'show_bar_values': True,    # Mostrar valores nas barras
            'show_acc_values': True,    # Mostrar valores acumulados
            'show_mean_label': True,    # Mostrar label da média
            'font_size_bars': 10,       # Tamanho fonte valores barras
            'font_size_acc': 10,        # Tamanho fonte valores acumulado
            'font_size_mean': 10        # Tamanho fonte média
        },
        'styling': {
            'title_size': 14,           # Tamanho título
            'label_size': 12,           # Tamanho labels eixos
            'tick_size': 10,            # Tamanho números eixos
            'title_pad': 20,            # Espaçamento título
            'bar_edge_width': 8,        # Espessura borda barras
            'marker_edge_width': 2,     # Espessura borda pontos
            'mean_line_style': '--',    # Estilo linha média
            'mean_line_width': 1.5,     # Espessura linha média
            'spine_color': '#69696F',   # Cor das linhas dos eixos
            'spine_width': 0.5          # Espessura das linhas dos eixos
        },
        'bar_radius': 0.5              # Raio para arredondamento das barras
    }
    
    # Mesclar configurações personalizadas
    if config:
        for key, value in config.items():
            if isinstance(value, dict) and key in default_config:
                default_config[key].update(value)
            else:
                default_config[key] = value
    
    cfg = default_config
    
    # Dados hipotéticos - CORRIGIDO: agora são valores de geração de caixa mensal
    meses = ['Janeiro', 'Fevereiro', 'Março']
    geracao_caixa = [227413.02, -94153.03, 83828.08]  # Valores mensais
    
    # Calcular valores acumulados - CORRIGIDO: acumulado é a soma progressiva
    acumulado = np.cumsum(geracao_caixa)
    
    # Calcular média da geração de caixa
    media = np.mean(geracao_caixa)
    
    # Verde se positivo, laranja se negativo
    cores = [cfg['colors']['positive'] if valor >= 0 else cfg['colors']['negative'] 
             for valor in geracao_caixa]
    
    # Configurações do gráfico
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=cfg['figure_size'], dpi=cfg['dpi'])
    
    # Função para formatação de valores no eixo Y - CORRIGIDO: mostra valores completos
    def y_fmt(value, tick_number):
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # Criar barras - NOVA LÓGICA: todas as barras começam do 0
    barras = []
    for i, (val, cor) in enumerate(zip(geracao_caixa, cores)):
        # Sempre usar valor absoluto para altura da barra
        altura_barra = abs(val)
        
        # Todas as barras começam do 0 e vão para cima
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
    
    # Adicionar valores nas barras - CORRIGIDO: mostra valores completos
    if cfg['annotations']['show_bar_values']:
        for i, height in enumerate(geracao_caixa):
            # Posicionar no centro da barra verticalmente (sempre positivo para posicionamento)
            y_position = abs(height) / 2
            
            # Formatação brasileira para valores nas barras (manter sinal original)
            valor_formatado = f"R${height:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            ax.annotate(valor_formatado,
                        xy=(i, y_position),
                        ha='center', va='center', 
                        fontsize=cfg['annotations']['font_size_bars'], 
                        fontweight='bold',
                        color='black',
                        rotation=90)    # Rotação vertical
    
    # Criar linha de acumulado suavizada
    x = np.array(range(len(meses)))
    y = np.array(acumulado)
    
    # Suavização com spline
    x_smooth = np.linspace(x.min(), x.max(), 300)
    # Usar grau 1 para poucos pontos, ou k=min(2, len(meses)-1) para ser flexível
    k = min(2, len(meses)-1)
    if len(meses) > 2:
        spl = make_interp_spline(x, y, k=k)
        y_smooth = spl(x_smooth)
        
        # Plotar linha de acumulado
        line = ax.plot(x_smooth, y_smooth, 
                      color=cfg['colors']['accumulated'], 
                      linewidth=cfg['line_width'], 
                      zorder=4)
    else:
        # Se houver poucos pontos, plotar linha direta
        line = ax.plot(x, y, 
                      color=cfg['colors']['accumulated'], 
                      linewidth=cfg['line_width'], 
                      zorder=4)
    
    # Adicionar pontos de acumulado
    scatter = ax.scatter(x, y, 
                        s=cfg['marker_size'], 
                        color=cfg['colors']['accumulated_points'],
                        edgecolor='white', 
                        linewidth=cfg['styling']['marker_edge_width'], 
                        zorder=5)
    
    # Adicionar valores de acumulado - CORRIGIDO: mostra valores completos
    if cfg['annotations']['show_acc_values']:
        for i, valor in enumerate(acumulado):
            # Formatação brasileira para valores acumulados
            valor_formatado = f"R${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            ax.annotate(valor_formatado, 
                       (i, valor), 
                       textcoords="offset points", 
                       xytext=(0,10), 
                       ha='center', 
                       fontsize=cfg['annotations']['font_size_acc'],
                       fontweight='bold',
                       color=cfg['colors']['accumulated'])
    
    # Linha de média tracejada (só mostrar se for positiva)
    if media >= 0:
        mean_line = ax.axhline(media, 
                              color=cfg['colors']['mean_line'],
                              linestyle=cfg['styling']['mean_line_style'], 
                              linewidth=cfg['styling']['mean_line_width'], 
                              zorder=2)
        
        # Adicionar label da média - NOVO: posição no espaço extra criado
        if cfg['annotations']['show_mean_label']:
            # Formatação brasileira para a média
            media_formatada = f"Média: R${media:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            # Posicionar no espaço extra criado à direita
            posicao_x_media = len(meses) - 0.2  # Posição no espaço extra
            
            ax.annotate(media_formatada, 
                        (posicao_x_media, media), 
                        ha='left',       # Alinhado à esquerda
                        va='center',     # Centralizado verticalmente na linha
                        fontsize=cfg['annotations']['font_size_mean'],
                        fontweight='bold',
                        color=cfg['colors']['mean_line'],
                        bbox=dict(boxstyle="round,pad=0.3", 
                                 facecolor='#FFFFFF', 
                                 edgecolor=cfg['colors']['mean_line'],
                                 alpha=1.0))  # Caixa de fundo totalmente opaca (fosca)
    
    # ESTENDER O EIXO X para criar espaço para o texto da média
    ax.set_xlim(-0.5, len(meses) + 0.5)  # Adiciona 1 unidade extra à direita
    
    # Personalização do eixo Y - NOVA LÓGICA: começar sempre do 0
    y_max_barras = max([abs(val) for val in geracao_caixa])  # Maior valor absoluto das barras
    y_max_acumulado = max(acumulado) if max(acumulado) > 0 else 0  # Maior valor acumulado positivo
    y_max = max(y_max_barras, y_max_acumulado) * cfg['margins']['top']
    
    ax.set_ylim(0, y_max)  # Sempre começar do 0
    
    # Removendo bordas
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    
    # Estilizando as bordas
    ax.spines["bottom"].set_color(cfg['styling']['spine_color'])
    ax.spines["left"].set_color(cfg['styling']['spine_color'])
    ax.spines["bottom"].set_linewidth(cfg['styling']['spine_width'])
    ax.spines["left"].set_linewidth(cfg['styling']['spine_width'])
    
    # Formatação dos valores no eixo Y
    ax.yaxis.set_major_formatter(FuncFormatter(y_fmt))
    
    # Configuração dos ticks
    ax.tick_params(axis='both', which='major', length=0, 
                  labelcolor=cfg['styling']['spine_color'], pad=12)
    
    # Configurar eixo X - IMPORTANTE: definir apenas os ticks dos meses
    ax.set_xticks(range(len(meses)))  # Apenas as posições dos meses
    ax.set_xticklabels(meses)         # Apenas os nomes dos meses
    ax.set_axisbelow(True)
    
    # Remover grid
    ax.grid(False)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Converter para base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=cfg['dpi'])
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

# Usar configuração padrão
histogram_base64 = generate_histogram_base64()