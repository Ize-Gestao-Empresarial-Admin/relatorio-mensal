#src/interfaces/streamlit_ui.py
import streamlit as st
from datetime import date, timedelta
from src.database.db_utils import DatabaseConnection, buscar_clientes, obter_meses
from src.core.indicadores import Indicadores
from src.core.relatorios import (
    Relatorio1, Relatorio2, Relatorio3, Relatorio4, Relatorio5, Relatorio6, Relatorio7, Relatorio8  # Adicionei Relatorio8
)
from src.rendering.engine import RenderingEngine
import os

def main():
    st.set_page_config(page_title="IZE Relatórios Financeiros", page_icon="📊", layout="centered")
    
    # Estilo personalizado
    st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; color: #0f52ba; text-align: center; margin-bottom: 2rem; }
    .subheader { font-size: 1.5rem; color: #333; margin-top: 1.5rem; margin-bottom: 1rem; }
    </style>
    """, unsafe_allow_html=True)
    
    # Logo da empresa
    logo_path = "assets/images/logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    
    # Título principal
    st.markdown("<h1 class='main-header'>Relatório Mensal</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Colunas para organização
    col1, col2 = st.columns(2)
    
    # Conexão com o banco
    db = DatabaseConnection()
    
    # Seleção de cliente
    with col1:
        st.subheader("Selecione o Cliente")
        clientes = buscar_clientes(db)
        cliente_options = {cliente['nome']: cliente['id_cliente'] for cliente in clientes}
        cliente_nome = st.selectbox("Cliente", list(cliente_options.keys()))
        cliente_id = cliente_options[cliente_nome]
    
    # Seleção de mês e ano
    with col2:
        st.subheader("Período do Relatório")
        meses = obter_meses()
        mes_nome = st.selectbox("Mês", [m[0] for m in meses])
        mes = next(m[1] for m in meses if m[0] == mes_nome)
        ano = date.today().year
    
    # Opção para gerar relatório completo ou selecionar relatórios individuais
    modo_relatorio = st.radio(
        "Modo de Geração",
        ["Relatório Completo", "Selecionar Relatórios Individuais"]
    )
    
    if modo_relatorio == "Selecionar Relatórios Individuais":
        # Seleção de relatórios
        st.markdown("<h2 class='subheader'>Selecione os Relatórios</h2>", unsafe_allow_html=True)
        relatorios_opcoes = [
            "Relatório 1 - Análise de Fluxo de Caixa 1",
            "Relatório 2 - Análise de Fluxo de Caixa 2",
            "Relatório 3 - Análise de Fluxo de Caixa 3",
            "Relatório 4 - Análise de Fluxo de Caixa 4",
            "Relatório 5 - Fechamento de Fluxo de Caixa",
            "Relatório 6 - Análise por Competência - DRE",
            "Relatório 7 - Indicadores",
            "Relatório 8 - Parecer Técnico (Nota do Consultor)"
        ]
        relatorios_selecionados = st.multiselect("Relatórios", relatorios_opcoes, default=["Relatório 1 - Análise de Fluxo de Caixa 1"])
    else:
        # Se for relatório completo, seleciona todos
        relatorios_opcoes = [
            "Relatório 1 - Análise de Fluxo de Caixa 1",
            "Relatório 2 - Análise de Fluxo de Caixa 2",
            "Relatório 3 - Análise de Fluxo de Caixa 3",
            "Relatório 4 - Análise de Fluxo de Caixa 4",
            "Relatório 5 - Fechamento de Fluxo de Caixa",
            "Relatório 6 - Análise por Competência - DRE",
            "Relatório 7 - Indicadores",
            "Relatório 8 - Parecer Técnico (Nota do Consultor)"
        ]
        relatorios_selecionados = relatorios_opcoes
        st.info("O relatório completo incluirá todas as 8 seções.")
    
    # Campo para parecer técnico (Relatório 8)
    if "Relatório 8 - Parecer Técnico (Nota do Consultor)" in relatorios_selecionados:
        st.markdown("<h2 class='subheader'>Parecer Técnico (Nota do Consultor)</h2>", unsafe_allow_html=True)
        analise_text = st.text_area("Insira o parecer técnico", height=200)
    else:
        analise_text = ""
    
    # Botão de geração
    if st.button("Gerar e Baixar Relatório PDF"):
        with st.spinner("Gerando relatório, por favor aguarde..."):
            try:
                indicadores = Indicadores(cliente_id, db)
                relatorios_classes = {
                    "Relatório 1 - Análise de Fluxo de Caixa 1": Relatorio1,
                    "Relatório 2 - Análise de Fluxo de Caixa 2": Relatorio2,
                    "Relatório 3 - Análise de Fluxo de Caixa 3": Relatorio3,
                    "Relatório 4 - Análise de Fluxo de Caixa 4": Relatorio4,
                    "Relatório 5 - Fechamento de Fluxo de Caixa": Relatorio5,
                    "Relatório 6 - Análise por Competência - DRE": Relatorio6,
                    "Relatório 7 - Indicadores": Relatorio7,
                    "Relatório 8 - Parecer Técnico (Nota do Consultor)": Relatorio8  # Usa a nova classe Relatorio8
                }
                
                relatorios_dados = []
                mes_atual = date(ano, mes, 1)
                mes_anterior = (mes_atual - timedelta(days=1)).replace(day=1)
                
                for rel_nome in relatorios_selecionados:
                    rel_class = relatorios_classes[rel_nome]
                    relatorio = rel_class(indicadores, cliente_nome)
                    
                    if rel_nome in [
                        "Relatório 1 - Análise de Fluxo de Caixa 1",
                        "Relatório 2 - Análise de Fluxo de Caixa 2",
                        "Relatório 3 - Análise de Fluxo de Caixa 3"
                    ]:
                        dados = relatorio.gerar_relatorio(mes_atual, mes_anterior)
                    elif rel_nome == "Relatório 8 - Parecer Técnico (Nota do Consultor)" and analise_text:
                        relatorio.salvar_analise(mes_atual, analise_text)
                        dados = relatorio.gerar_relatorio(mes_atual)
                    else:
                        dados = relatorio.gerar_relatorio(mes_atual)
                    
                    relatorios_dados.append((rel_nome, dados))
                
                # Usar o novo motor de renderização
                rendering_engine = RenderingEngine()
                output_filename = f"Relatorio_{cliente_nome.replace(' ', '_')}_{mes_nome}_{ano}.pdf"
                output_path = os.path.join("outputs", output_filename)
                
                pdf_path = rendering_engine.render_to_pdf(
                    relatorios_dados, 
                    cliente_nome, 
                    mes_nome, 
                    ano, 
                    output_path
                )
                
                st.success("Relatório gerado com sucesso!")
                
                # Botão de download
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