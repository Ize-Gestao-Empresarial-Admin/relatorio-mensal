import streamlit as st
from streamlit_quill import st_quill
from datetime import date, timedelta
from src.database.db_utils import DatabaseConnection, buscar_clientes, obter_meses, obter_anos
from src.core.indicadores import Indicadores
from src.core.relatorios import (
    Relatorio1, Relatorio2, Relatorio3, Relatorio4, Relatorio5, Relatorio6, Relatorio7, Relatorio8
)
from src.rendering.engine import RenderingEngine
import os
import re
import time

def processar_html_parecer(html_content: str) -> str:
    """Processa o HTML do editor Quill para torná-lo compatível com PDF"""
    if not html_content:
        return ""
    
    # Mapear classes do Quill para CSS inline
    size_mapping = {
        'ql-size-small': 'font-size: 12px;',
        'ql-size-normal': 'font-size: 14px;',
        'ql-size-large': 'font-size: 20px;',
        'ql-size-huge': 'font-size: 24px;'
    }
    
    # Substituir classes por CSS inline
    processed_html = html_content
    for quill_class, css_style in size_mapping.items():
        # Procurar por spans com a classe específica
        pattern = rf'<span class="{quill_class}">(.*?)</span>'
        replacement = rf'<span style="{css_style}">\1</span>'
        processed_html = re.sub(pattern, replacement, processed_html, flags=re.DOTALL)
    
    return processed_html

def render_parecer_tecnico(relatorios_selecionados: list) -> str:
    """Renderiza o editor de texto rico para o Parecer Técnico se o Relatório 8 estiver selecionado."""
    RELATORIO_8 = "Relatório 8"
    if RELATORIO_8 in relatorios_selecionados:
        st.markdown("<h2 class='subheader'>Parecer Técnico (Nota do Consultor)</h2>", unsafe_allow_html=True)
        st.markdown("Use os botões abaixo para formatar o texto (negrito, itálico, tamanho da fonte).", unsafe_allow_html=True)
        
        # Configuração do editor Quill
        content = st_quill(
            placeholder="Digite aqui suas observações e análises...",
            toolbar=[
                ["bold"], 
                [{"list": "bullet"}],
                [{"size": ["small", False, "large", "huge"]}]
            ],
            key="quill_editor",
            html=True  # Retorna o conteúdo como HTML
        )
        
        # Processar o HTML para torná-lo compatível com PDF
        return processar_html_parecer(content)
    return ""

def main():
    # Configurar a página
    st.set_page_config(page_title="IZE Relatórios Financeiros", page_icon="📊", layout="centered")
    
    # Estilo personalizado
    st.markdown("""
    <style>
    
    ._linkOutText_1upux_17 {
        display: none !important;
    }
    
    .main-header { font-size: 2.5rem; color: #0f52ba; text-align: center; margin-bottom: 2rem; }
    .subheader { font-size: 1.5rem; color: #333; margin-top: 1.5rem; margin-bottom: 1rem; }
    .dev-note { font-style: italic; color: #666; font-size: 0.9rem; }
    .user-info { background-color: #e3f2fd; padding: 0.5rem; border-radius: 5px; margin-bottom: 1rem; }
    </style>
    """, unsafe_allow_html=True)
    
    # Logo da empresa
    logo_path = "assets/images/logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    
    # Título principal
    st.markdown("<h1 class='main-header'>Relatório Mensal</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Conexão com o banco
    db = DatabaseConnection()
    
    # Inicializar session_state para armazenar cliente_id
    if 'cliente_id' not in st.session_state:
        st.session_state.cliente_id = None
    
    # Seleção de cliente
    st.markdown("<h3 class='subheader'>Selecione o Cliente</h3>", unsafe_allow_html=True)
    clientes = buscar_clientes(db)
    if not clientes:
        st.error("Nenhum cliente ativo encontrado no banco de dados.")
        return
    
    # Opção para múltiplos clientes
    multi_cliente = st.checkbox(
        "Agrupar dados de múltiplos clientes em um único relatório",
        help="Consolida dados de clientes com mais de um ID no banco"
    )
    
    cliente_options = {cliente['nome']: cliente['id_cliente'] for cliente in clientes}
    
    if multi_cliente:
        # Seleção múltipla de clientes
        cliente_nomes = st.multiselect(
            "Clientes",
            list(cliente_options.keys()),
            default=[list(cliente_options.keys())[0]] if cliente_options else [],
            help="Selecione um ou mais clientes para agrupar dados em um único relatório"
        )
        
        if not cliente_nomes:
            st.warning("Selecione pelo menos um cliente")
            cliente_nomes = [list(cliente_options.keys())[0]] if cliente_options else []
        
        # Gerar nome exibido para o cliente
        display_cliente_nome = f"{cliente_nomes[0]}_Consolidado" if len(cliente_nomes) > 1 else cliente_nomes[0]
        
        # Lista de IDs dos clientes
        cliente_ids = [cliente_options[nome] for nome in cliente_nomes]
        cliente_id = cliente_ids[0]  # Primeiro ID para compatibilidade
    else:
        # Seleção única de cliente (comportamento original)
        cliente_nome = st.selectbox(
            "Cliente",
            list(cliente_options.keys()),
            key="cliente_select",
            help="Selecione o cliente para gerar o relatório."
        )
        cliente_id = cliente_options[cliente_nome]
        display_cliente_nome = cliente_nome
        cliente_ids = [cliente_id]
    
    # Atualizar session_state
    st.session_state.cliente_id = cliente_id
    st.session_state.cliente_ids = cliente_ids
    st.session_state.multi_cliente = multi_cliente
    st.session_state.display_cliente_nome = display_cliente_nome
    
    # Seleção de mês e ano
    st.markdown("<h3 class='subheader'>Período do Relatório</h3>", unsafe_allow_html=True)
    col_periodo1, col_periodo2 = st.columns([1, 1])
    
    with col_periodo1:
        meses = obter_meses()
        mes_nome = st.selectbox(
            "Mês",
            [m[0] for m in meses],
            key="mes_select",
            help="Selecione o mês do relatório (por padrão selecionado o mês anterior ao atual)",
            index=(date.today().month - 2) % 12
        )
        mes = next(m[1] for m in meses if m[0] == mes_nome)
    
    with col_periodo2:
        # Se for multi-cliente, busque anos de todos os clientes selecionados
        if multi_cliente and cliente_ids:
            todos_anos = []
            for id_cliente in cliente_ids:
                anos_cliente = obter_anos(db, id_cliente)
                todos_anos.extend(anos_cliente)
            # Remove duplicados e ordena
            anos = sorted(list(set(todos_anos)), reverse=True)
        else:
            anos = obter_anos(db, cliente_id)
            
        ano = st.selectbox(
            "Ano",
            anos,
            index=0,
            key="ano_select",
            help="Selecione o ano do relatório (por padrão selecionado o ano atual)."
        )
    
    # Definição dos relatórios com agrupamento
    relatorios_display = {
        "Fluxo de Caixa": [
            {"id": "Relatório 1", "nome": "Relatório 1 - Análise de Fluxo de Caixa 1", "status": "ativo"},
            {"id": "Relatório 2", "nome": "Relatório 2 - Análise de Fluxo de Caixa 2", "status": "ativo"},
            {"id": "Relatório 3", "nome": "Relatório 3 - Análise de Fluxo de Caixa 3", "status": "ativo"},
            {"id": "Relatório 4", "nome": "Relatório 4 - Análise de Fluxo de Caixa 4", "status": "ativo"},
            {"id": "Relatório 5", "nome": "Relatório 5 - Fechamento de Fluxo de Caixa", "status": "ativo"}
        ],
        "DRE": [
            {"id": "Relatório 6", "nome": "Relatório 6 - Análise por Competência - DRE", "status": "ativo"}
        ],
        "Indicadores": [
            {"id": "Relatório 7", "nome": "Relatório 7 - Indicadores", "status": "ativo"}
        ]
    }
    
    # Opção para gerar relatório completo ou selecionar relatórios individuais
    modo_relatorio = st.radio(
        "Modo de Geração",
        ["Relatório Completo", "Selecionar Relatórios Individuais"],
        key="modo_relatorio"
    )
    
    # Checkbox para incluir a Nota do Consultor
    st.markdown("<h3 class='subheader'>Opções</h3>", unsafe_allow_html=True)
    incluir_parecer = st.checkbox(
        "Inserir a Nota do Consultor",
        value=False,
        key="incluir_parecer"
    )
    
    if modo_relatorio == "Selecionar Relatórios Individuais":
        st.markdown("<h3 class='subheader'>Selecione os relatórios</h3>", unsafe_allow_html=True)
        agrupamentos_opcoes = list(relatorios_display.keys())
        agrupamentos_selecionados = st.multiselect(
            "Agrupamentos",
            agrupamentos_opcoes,
            default=["Fluxo de Caixa"]
        )
        
        # Mapear agrupamentos para relatórios
        relatorios_selecionados = []
        for grupo in agrupamentos_selecionados:
            for relatorio in relatorios_display[grupo]:
                relatorios_selecionados.append(relatorio["id"])
        
        if incluir_parecer:
            relatorios_selecionados.append("Relatório 8")
    else:
        relatorios_selecionados = [
            "Relatório 1", "Relatório 2", "Relatório 3", "Relatório 4",
            "Relatório 5", "Relatório 6", "Relatório 7"
        ]
        if incluir_parecer:
            relatorios_selecionados.append("Relatório 8")
    
    analise_text = render_parecer_tecnico(relatorios_selecionados)
    
    # Quando o botão "Gerar e Baixar Relatório PDF" for clicado:
    if st.button("Gerar e Baixar Relatório PDF", key="gerar_relatorio"):
        if not relatorios_selecionados:
            st.error("Selecione pelo menos um agrupamento ou a Nota do Consultor para gerar o PDF.")
            return

        with st.spinner("Gerando relatório, por favor aguarde..."):
            start_total = time.time()
            st.info("🚀 Iniciando geração do relatório...")
            
            try:
                # Cria uma instância de indicadores com os ids de clientes escolhidos
                indicadores = Indicadores(cliente_ids, db)  # Passar cliente_ids diretamente
                
                relatorios_classes = {
                    "Relatório 1": Relatorio1,
                    "Relatório 2": Relatorio2,
                    "Relatório 3": Relatorio3,
                    "Relatório 4": Relatorio4,
                    "Relatório 5": Relatorio5,
                    "Relatório 6": Relatorio6,
                    "Relatório 7": Relatorio7,
                    "Relatório 8": Relatorio8
                }
                
                relatorios_dados = []
                mes_atual = date(ano, mes, 1)
                mes_anterior = (mes_atual - timedelta(days=1)).replace(day=1)
                
                marca = "Sim"
                
                # Mapear agrupamentos para o índice
                indice_data = {
                    "fluxo_caixa": "Sim" if any(r in relatorios_selecionados for r in ["Relatório 1", "Relatório 2", "Relatório 3", "Relatório 4", "Relatório 5"]) else "Não",
                    "dre_gerencial": "Sim" if "Relatório 6" in relatorios_selecionados else "Não",
                    "indicador": "Sim" if "Relatório 7" in relatorios_selecionados else "Não",
                    "nota_consultor": "Sim" if "Relatório 8" in relatorios_selecionados else "Não",
                    "cliente_nome": display_cliente_nome,
                    "mes": mes_nome,
                    "ano": ano,
                    "nome": display_cliente_nome,  # Nome para o template
                    "Periodo": f"{mes_nome} {ano}",  # Período para o template
                    "marca": marca
                }
                relatorios_dados.append(("Índice", indice_data))
                
                for rel_nome in relatorios_selecionados:
                    rel_class = relatorios_classes[rel_nome]
                    relatorio = rel_class(indicadores, display_cliente_nome)
                    
                    if rel_nome in ["Relatório 1", "Relatório 2", "Relatório 3", "Relatório 4"]:
                        dados = relatorio.gerar_relatorio(mes_atual, mes_anterior)
                    elif rel_nome == "Relatório 8":
                        if analise_text:
                            relatorio.salvar_analise(mes_atual, analise_text)
                        dados = relatorio.gerar_relatorio(mes_atual)
                    else:
                        dados = relatorio.gerar_relatorio(mes_atual)
                    
                    relatorios_dados.append((rel_nome, dados))
                
                rendering_engine = RenderingEngine()
                output_filename = f"Relatorio_{display_cliente_nome.replace(' ', '_')}_{mes_nome}_{ano}.pdf"
                output_path = os.path.join("outputs", output_filename)
                
                os.makedirs("outputs", exist_ok=True)  # Criar diretório se não existir
                
                pdf_path = rendering_engine.render_to_pdf(
                    relatorios_dados, 
                    display_cliente_nome, 
                    mes_nome, 
                    ano, 
                    output_path
                )
                
                total_time = time.time() - start_total
                st.success(f"✅ Relatório gerado com sucesso em {total_time:.2f}s!")
                
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Baixar Relatório PDF",
                        data=f,
                        file_name=output_filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
            except Exception as e:
                st.error(f"Erro ao gerar relatório: {str(e)}")
                st.exception(e)
                st.warning("Certifique-se de que o wkhtmltopdf está instalado e no PATH do sistema.")

if __name__ == "__main__":
    main()