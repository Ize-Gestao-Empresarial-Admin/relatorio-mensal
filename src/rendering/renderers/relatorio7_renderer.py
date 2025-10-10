from typing import Dict, Any, List, Tuple, Union
from src.rendering.renderers.base_renderer import BaseRenderer
import os
import base64
import logging
import math
import numpy as np

logger = logging.getLogger(__name__)

class Relatorio7Renderer(BaseRenderer):
    """Renderizador específico para o Relatório 7 - Indicadores."""
    
    def __init__(self):
        super().__init__()
        # Carregar o template principal do relatório 7
        self.template = self.env.get_template("relatorio7/template.html")
        # Carregar o fragmento para páginas adicionais
        self.page_fragment = self.env.get_template("relatorio7/page_fragment.html")

    def _determine_performance(self, indicador_info):
        """Determina a performance do indicador baseado nos cenários bom/ruim"""
        valor = indicador_info.get('valor', 0)
        cenario_bom = indicador_info.get('cenario_bom')
        cenario_ruim = indicador_info.get('cenario_ruim')
        
        # Verificar se os cenários são válidos (não NaN, não None e não 0)
        cenario_bom_valido = cenario_bom is not None and not (isinstance(cenario_bom, float) and math.isnan(cenario_bom)) and cenario_bom != 0
        cenario_ruim_valido = cenario_ruim is not None and not (isinstance(cenario_ruim, float) and math.isnan(cenario_ruim)) and cenario_ruim != 0
        
        # Se não temos cenários válidos, retornar 'neutro'
        if not cenario_bom_valido or not cenario_ruim_valido:
            return 'neutro'
        
        # Lógica de comparação com cenários
        if valor >= cenario_bom:
            return 'positivo'  # Verde
        elif valor <= cenario_ruim:
            return 'negativo'  # Laranja
        else:
            # Valor está entre cenário ruim e bom
            return 'neutro'  # Cinza

    def _get_header_color(self, performance):
        """Retorna a cor do header baseada na performance"""
        color_map = {
            'positivo': "#009F64",  # Verde
            'negativo': "#E75F00",  # Laranja
            'neutro': "#A5A5A5"     # Cinza
        }
        return color_map.get(performance, "#A5A5A5")
    
    def _get_icon_base64(self, indicador_info):
        """Determina qual ícone usar baseado no tipo e performance do indicador"""
        icons_dir = os.path.abspath("assets/icons")
        
        unidade = indicador_info.get('unidade', 'SU')
        
        # Usar a nova lógica de performance
        performance = self._determine_performance(indicador_info)
        
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
        icon_path = os.path.join(icons_dir, icon_file)
        
        try:
            with open(icon_path, "rb") as f:
                return base64.b64encode(f.read()).decode("ascii")
        except FileNotFoundError:
            logger.warning(f"Ícone não encontrado: {icon_path}. Usando ícone padrão.")
            # Usar ícone padrão (SU cinza)
            default_path = os.path.join(icons_dir, 'LOGO-SU-CINZA.png')
            try:
                with open(default_path, "rb") as f:
                    return base64.b64encode(f.read()).decode("ascii")
            except:
                return ""  # Retorna string vazia se não conseguir carregar nenhum ícone
    
    def _format_cenario_text(self, indicador):
        """Formata o texto de cenário bom/ruim"""
        bom = indicador.get('cenario_bom')
        ruim = indicador.get('cenario_ruim')
        unidade = indicador.get('unidade', 'SU')
        
        # Verificar se os valores são válidos (não NaN e não None)
        bom_valido = bom is not None and not (isinstance(bom, float) and math.isnan(bom))
        ruim_valido = ruim is not None and not (isinstance(ruim, float) and math.isnan(ruim))
        
        # Se algum valor não é válido, retornar cenário não definido
        if not bom_valido or not ruim_valido:
            return "Cenário não definido"
        
        # Se AMBOS os valores são zero, retornar cenário não definido
        if bom == 0 and ruim == 0:
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
    
    def _format_valor_display(self, valor, unidade):
        """Formata o valor para exibição"""
        if unidade == '%':
            valor_para_formatar = valor * 100
            return f"{valor_para_formatar:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
        elif unidade == 'R$':
            return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        else:  # SU
            return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def _calculate_dynamic_sizes(self, nome, valor, bom=None):
        """Calcula tamanhos dinâmicos para nome e valor baseado no tamanho do conteúdo"""
        nome_length = len(nome)
        
        # Estimar se o nome vai quebrar em 3 linhas (aproximadamente 18 caracteres por linha)
        caracteres_por_linha = 18
        linhas_estimadas = math.ceil(nome_length / caracteres_por_linha)
        
        # Tamanho da fonte e posição do texto baseado no comprimento do nome
        if linhas_estimadas >= 3 or nome_length > 54:  # 3 linhas * 18 chars = 54
            nome_font_size = "11px"  # Reduzir fonte se for quebrar em 3 linhas
            text_top = "15px"
        elif nome_length > 40:
            nome_font_size = "13px" 
            text_top = "20px"
        elif nome_length > 30:
            nome_font_size = "14px"
            text_top = "22px"
        else:
            nome_font_size = "16px"
            text_top = "27px"
        
        # Tamanho da fonte do valor baseado no tamanho do número
        # Se passa de milhão (1.000.000) e tem casas decimais significativas
        if abs(valor) >= 1000000:
            # Verificar se tem casas decimais significativas (não são .00)
            parte_decimal = valor - int(valor)
            if abs(parte_decimal) > 0.01:  # Tem decimais significativos
                valor_font_size = "14px"
            else:
                valor_font_size = "16px"
        elif abs(valor) >= 999999999:
            valor_font_size = "15px"
        else:
            valor_font_size = "18px"
        
        # Tamanho da fonte do cenário baseado no valor do "bom"
        if bom is not None and not (isinstance(bom, float) and math.isnan(bom)):
            cenario_font_size = "7px" if bom >= 10000000 else "8px"
        else:
            cenario_font_size = "8px"
        
        # Log para debugging casos problemáticos
        if linhas_estimadas >= 3 or abs(valor) >= 1000000:
            logger.debug(f"Ajuste: '{nome[:30]}...' (len={nome_length}, ~{linhas_estimadas} linhas) = {valor:,.2f} | "
                        f"Nome: {nome_font_size}, Valor: {valor_font_size}")
        
        return {
            'nome_font_size': nome_font_size,
            'text_top': text_top,
            'valor_font_size': valor_font_size,
            'cenario_font_size': cenario_font_size
        }

    def _dividir_indicadores_em_paginas(self, indicadores_processados, indicadores_por_pagina=24):
        """Divide os indicadores em grupos para páginas separadas"""
        paginas = []
        total_indicadores = len(indicadores_processados)
        
        for i in range(0, total_indicadores, indicadores_por_pagina):
            grupo = indicadores_processados[i:i + indicadores_por_pagina]
            numero_pagina = (i // indicadores_por_pagina) + 1
            total_paginas = math.ceil(total_indicadores / indicadores_por_pagina)
            
            paginas.append({
                'indicadores': grupo,
                'numero_pagina': numero_pagina,
                'total_paginas': total_paginas,
                'eh_primeira_pagina': numero_pagina == 1,
                'eh_ultima_pagina': numero_pagina == total_paginas
            })
        
        logger.info(f"Divididos {total_indicadores} indicadores em {len(paginas)} páginas")
        return paginas
    
    def render(self, data: Union[List[Dict[str, Any]], Tuple[List[Dict[str, Any]], Dict[str, str]]], 
               cliente_nome: str, mes_nome: str, ano: int) -> str:
        """
        Renderiza os dados do Relatório 7 em HTML usando templates separados por página.
        Template1 = primeira página (até 24 indicadores)
        Template2 = páginas subsequentes (24 indicadores cada)

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
            indicadores_data, notas_data = data
            sem_indicadores = notas_data.get("sem_indicadores", False)
        else:
            indicadores_data = data
            sem_indicadores = False
        
        # Carregar rodapé (será usado em ambos os templates)
        icons_dir = os.path.abspath("assets/icons")
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
        
        # Se não há indicadores, renderizar apenas a primeira página vazia
        if sem_indicadores or not indicadores_data:
            logger.info(f"Renderizando Relatório 7 sem indicadores para cliente {cliente_nome}")
            
            template_data = {
                "nome": cliente_nome,
                "Periodo": f"{mes_nome}/{ano}",
                "sem_indicadores": True,
                "paginas": [{
                    'indicadores': [],
                    'numero_pagina': 1,
                    'total_paginas': 1,
                    'eh_primeira_pagina': True,
                    'eh_ultima_pagina': True
                }],
                "total_indicadores": 0
            }
            
            return self.template.render(
                data=template_data,
                icon_rodape=icon_rodape,
                cliente_nome=cliente_nome,
                mes_nome=mes_nome,
                ano=ano
            )
        
        # Processar cada indicador
        indicadores_processados = []
        for indicador in indicadores_data:
            nome = indicador.get('categoria', '')
            valor = indicador.get('valor', 0)
            unidade = indicador.get('unidade', 'SU')
            cenario_bom = indicador.get('cenario_bom')
            cenario_ruim = indicador.get('cenario_ruim')
            
            # Determinar performance baseada nos cenários
            performance = self._determine_performance(indicador)
            header_color = self._get_header_color(performance)
            
            # Calcular tamanhos dinâmicos
            sizes = self._calculate_dynamic_sizes(nome, valor, cenario_bom)
            
            # Processar dados do indicador
            indicador_processado = {
                'nome': nome,
                'valor': valor,
                'unidade': unidade,
                'cenario_bom': cenario_bom,
                'cenario_ruim': cenario_ruim,
                'valor_formatado': self._format_valor_display(valor, unidade),
                'cenario_texto': self._format_cenario_text(indicador),
                'icon_base64': self._get_icon_base64(indicador),
                'header_color': header_color,
                'performance': performance,
                'nome_font_size': sizes['nome_font_size'],
                'text_top': sizes['text_top'],
                'valor_font_size': sizes['valor_font_size'],
                'cenario_font_size': sizes['cenario_font_size']
            }
            indicadores_processados.append(indicador_processado)
            
            logger.debug(f"Indicador processado: {nome} = {indicador_processado['valor_formatado']} - Performance: {performance}")
        
        # Configuração de páginas
        indicadores_por_pagina = 24  # Limite de indicadores por página
        total_indicadores = len(indicadores_processados)
        
        # LÓGICA SIMPLIFICADA: TEMPLATES INDEPENDENTES
        
        # Se cabem todos na primeira página (≤ 24 indicadores)
        if total_indicadores <= indicadores_por_pagina:
            logger.info(f"Renderizando {total_indicadores} indicadores em 1 página (template1)")
            
            # Usar apenas template1
            paginas = [{
                'indicadores': indicadores_processados,
                'numero_pagina': 1,
                'total_paginas': 1,
                'eh_primeira_pagina': True,
                'eh_ultima_pagina': True
            }]
            
            template_data = {
                "nome": cliente_nome,
                "Periodo": f"{mes_nome}/{ano}",
                "sem_indicadores": False,
                "paginas": paginas,
                "total_indicadores": total_indicadores
            }
            
            return self.template.render(
                data=template_data,
                icon_rodape=icon_rodape,
                cliente_nome=cliente_nome,
                mes_nome=mes_nome,
                ano=ano
            )
        
        # Se precisamos de múltiplas páginas (> 24 indicadores)
        else:
            logger.info(f"Renderizando {total_indicadores} indicadores em múltiplas páginas")
            
            # Dividir indicadores
            primeira_pagina_indicadores = indicadores_processados[:indicadores_por_pagina]
            indicadores_restantes = indicadores_processados[indicadores_por_pagina:]
            
            # Calcular total de páginas
            total_paginas = math.ceil(total_indicadores / indicadores_por_pagina)
            
            logger.info(f"Primeira página: {len(primeira_pagina_indicadores)} indicadores")
            logger.info(f"Páginas restantes: {len(indicadores_restantes)} indicadores em {total_paginas - 1} páginas")
            
            # RENDERIZAR apenas a primeira página com o template principal
            paginas_primeira = [{
                'indicadores': primeira_pagina_indicadores,
                'numero_pagina': 1,
                'total_paginas': total_paginas,
                'eh_primeira_pagina': True,
                'eh_ultima_pagina': False
            }]
            
            template_data_primeira = {
                "nome": cliente_nome,
                "Periodo": f"{mes_nome}/{ano}",
                "sem_indicadores": False,
                "paginas": paginas_primeira,
                "total_indicadores": len(primeira_pagina_indicadores)
            }
            
            # Renderizar template principal (com HTML, HEAD, CSS)
            html_completo = self.template.render(
                data=template_data_primeira,
                icon_rodape=icon_rodape,
                cliente_nome=cliente_nome,
                mes_nome=mes_nome,
                ano=ano
            )
            
            # ADICIONAR fragmentos de páginas adicionais (apenas conteúdo)
            for pagina_num in range(2, total_paginas + 1):
                inicio_idx = (pagina_num - 2) * indicadores_por_pagina
                fim_idx = inicio_idx + indicadores_por_pagina
                indicadores_pagina = indicadores_restantes[inicio_idx:fim_idx]
                
                if not indicadores_pagina:
                    continue
                
                logger.info(f"Renderizando página {pagina_num} com {len(indicadores_pagina)} indicadores (fragmento)")
                
                # Renderizar apenas o fragmento da página (sem html/head/body)
                fragmento_html = self.page_fragment.render(
                    indicadores=indicadores_pagina,
                    nome_relatorio=cliente_nome,
                    periodo=f"{mes_nome}/{ano}",
                    eh_primeira_pagina=False
                )
                
                # Inserir o fragmento antes do fechamento do </body>
                html_completo = html_completo.replace('</body>', fragmento_html + '\n</body>')
            
            logger.info(f"HTML completo gerado: {total_paginas} páginas em um único documento limpo")
            return html_completo
