import streamlit as st
from streamlit_quill import st_quill
from datetime import date, timedelta
import sys
import os
import re
import requests

# Garantir que o diretório raiz está no Python path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.database.db_utils import DatabaseConnection, buscar_clientes, obter_meses, obter_anos

# Configuração da API
API_URL = "https://ize-relatorios-api-1052359947797.southamerica-east1.run.app/v1/relatorios/pdf"
API_KEY = os.getenv("API_KEY", "tj8DbJ0bDYDwqLKhF4rEDKaoOW6KxIC6ofeDtc44aA_0XlOEZcu49zAQKYylodOZ")

def verificar_permissoes():
    """
    Verifica se o usuário tem permissão para acessar os relatórios
    baseado nos parâmetros da URL
    """
    # CORREÇÃO: Usar st.query_params em vez de st.experimental_get_query_params
    params = st.query_params
    
    # CORREÇÃO: st.query_params retorna valores diretamente, não listas
    is_admin = params.get('is_admin', 'false').lower() == 'true'
    is_consultant = params.get('is_consultant', 'false').lower() == 'true'
    user_id = params.get('user_id', '')
    user_name = params.get('user_name', '')
    
    # Verificar se tem permissão
    if not (is_admin or is_consultant):
        return False, user_name, is_admin, is_consultant
    
    return True, user_name, is_admin, is_consultant

def mostrar_acesso_negado(user_name=""):
    """Mostra a tela de acesso negado"""
    st.markdown("""
    <style>
    .access-denied-container {
        text-align: center;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        margin: 2rem 0;
    }
    .access-denied-title {
        color: #dc3545;
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    .access-denied-message {
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="access-denied-container">
        <h1 class="access-denied-title">🚫 Acesso Negado</h1>
        <p class="access-denied-message">Você não tem permissão para acessar os relatórios.</p>
        <p class="access-denied-message">Apenas administradores e consultores podem visualizar esta página.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if user_name:
        st.info(f"Usuário: {user_name}")
    
    st.markdown("---")
    st.markdown("**Entre em contato com o administrador do sistema para obter acesso.**")

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
    # PRIMEIRO: Configurar a página ANTES de qualquer outra coisa
    st.set_page_config(page_title="IZE Relatórios Financeiros", page_icon="📊", layout="centered")
    
    # SEGUNDO: Verificar permissões (SEM fazer st.write ainda)
    tem_permissao, user_name, is_admin, is_consultant = verificar_permissoes()
    
    if not tem_permissao:
        # Debug apenas se não tem permissão
        mostrar_acesso_negado(user_name)
        return
    
    # Se chegou até aqui, o usuário tem permissão - continua com o código original

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
    
    # Mostrar informações do usuário
    if user_name:
        st.markdown(f"<div class='user-info'>Seja bem-vindo(a) <strong>{user_name}</strong>! 🚀</div>", 
                   unsafe_allow_html=True)
    
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

        # NOVO: Aviso informativo sobre o tempo de processamento
        with st.spinner("Gerando relatório, por favor aguarde..."):
            # Adicionar informação sobre tempo estimado
            num_relatorios = len(relatorios_selecionados)
            tempo_estimado = "30 segundos a 2 minutos" if num_relatorios <= 4 else "2 a 5 minutos"
            st.info(f"⏱️ **Gerando relatório via API em nuvem...** Tempo estimado: {tempo_estimado}")
            
            try:
                # Mapear nomes dos relatórios para IDs
                relatorio_map = {
                    "Relatório 1": 1,
                    "Relatório 2": 2,
                    "Relatório 3": 3,
                    "Relatório 4": 4,
                    "Relatório 5": 5,
                    "Relatório 6": 6,
                    "Relatório 7": 7,
                    "Relatório 8": 8
                }
                
                relatorios_ids = [relatorio_map[r] for r in relatorios_selecionados]
                
                # Preparar payload para a API
                payload = {
                    "id_cliente": cliente_ids,
                    "mes": mes,
                    "ano": ano,
                    "relatorios": relatorios_ids,
                    "analise_text": analise_text if analise_text else ""
                }
                
                # Headers com autenticação
                headers = {
                    "X-API-Key": API_KEY,
                    "Content-Type": "application/json"
                }
                
                # Fazer requisição para a API
                with st.spinner("🔄 Conectando com a API e gerando PDF..."):
                    response = requests.post(
                        API_URL,
                        json=payload,
                        headers=headers,
                        timeout=600  # 10 minutos de timeout
                    )
                
                # Verificar resposta
                if response.status_code == 200:
                    st.success("✅ Relatório gerado com sucesso!")
                    
                    # Extrair nome do arquivo do header Content-Disposition
                    content_disposition = response.headers.get('Content-Disposition', '')
                    if 'filename=' in content_disposition:
                        filename = content_disposition.split('filename=')[1].strip('"')
                    else:
                        filename = f"Relatorio_{display_cliente_nome.replace(' ', '_')}_{mes_nome}_{ano}.pdf"
                    
                    # Botão de download
                    st.download_button(
                        label="📥 Baixar Relatório PDF",
                        data=response.content,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                elif response.status_code == 401:
                    st.error("🔒 Erro de autenticação: API Key inválida.")
                    st.warning("Entre em contato com o administrador do sistema.")
                    
                elif response.status_code == 422:
                    st.error("❌ Dados inválidos enviados para a API.")
                    try:
                        error_detail = response.json()
                        st.json(error_detail)
                    except:
                        st.text(response.text)
                        
                elif response.status_code == 503:
                    st.error("⚠️ Serviço temporariamente indisponível.")
                    st.warning("A API está sobrecarregada. Tente novamente em alguns instantes ou gere menos relatórios por vez.")
                    
                else:
                    st.error(f"❌ Erro ao gerar relatório: Status {response.status_code}")
                    try:
                        error_detail = response.json()
                        st.json(error_detail)
                    except:
                        st.text(response.text)
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Tempo limite excedido!")
                st.warning("A geração do relatório demorou muito. Tente com menos relatórios ou aguarde alguns minutos e tente novamente.")
                
            except requests.exceptions.ConnectionError:
                st.error("🌐 Erro de conexão com a API!")
                st.warning("Verifique sua conexão com a internet ou tente novamente mais tarde.")
                
            except Exception as e:
                st.error(f"❌ Erro inesperado: {str(e)}")
                st.exception(e)

if __name__ == "__main__":
    main()