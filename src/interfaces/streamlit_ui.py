#src/interfaces/streamlit_ui.py

import streamlit as st
from datetime import date, timedelta
from src.database.db_utils import DatabaseConnection, buscar_clientes, obter_meses
from src.core.indicadores import Indicadores
from src.core.relatorios import (
    Relatorio1, Relatorio2, Relatorio3, Relatorio4, Relatorio5, Relatorio6, Relatorio7
)
from src.interfaces.pdf_generator import PDFGenerator
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
    logo_path = "static/images/logo.png"
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
    
    # Seleção de relatórios
    st.markdown("<h2 class='subheader'>Selecione os Relatórios</h2>", unsafe_allow_html=True)
    relatorios_opcoes = [
        "Relatório 1 - Resultados Mensais",
        "Relatório 2 - Análise por Competência",
        "Relatório 3 - Análise de Lucros",
        "Relatório 4 - Evolução",
        "Relatório 5 - Indicadores",
        "Relatório 6 - Análise Qualitativa",
        "Relatório 7 - Imagens"
    ]
    relatorios_selecionados = st.multiselect("Relatórios", relatorios_opcoes, default=["Relatório 1 - Resultados Mensais"])
    
    # Campo para análise qualitativa (Relatório 6)
    if "Relatório 6 - Análise Qualitativa" in relatorios_selecionados:
        st.markdown("<h2 class='subheader'>Análise Qualitativa (Relatório 6)</h2>", unsafe_allow_html=True)
        analise_text = st.text_area("Insira a análise qualitativa", height=200)
    
    # Botão de geração
    if st.button("Gerar e Baixar Relatório PDF"):
        with st.spinner("Gerando relatório, por favor aguarde..."):
            try:
                indicadores = Indicadores(cliente_id, db)
                relatorios_classes = {
                    "Relatório 1 - Resultados Mensais": Relatorio1,
                    "Relatório 2 - Análise por Competência": Relatorio2,
                    "Relatório 3 - Análise de Lucros": Relatorio3,
                    "Relatório 4 - Evolução": Relatorio4,
                    "Relatório 5 - Indicadores": Relatorio5,
                    "Relatório 6 - Análise Qualitativa": Relatorio6,
                    "Relatório 7 - Imagens": Relatorio7
                }
                
                relatorios_dados = []
                mes_atual = date(ano, mes, 1)
                mes_anterior = (mes_atual - timedelta(days=1)).replace(day=1)
                
                for rel_nome in relatorios_selecionados:
                    rel_class = relatorios_classes[rel_nome]
                    relatorio = rel_class(indicadores, cliente_nome)
                    
                    if rel_nome in ["Relatório 1 - Resultados Mensais", "Relatório 2 - Análise por Competência", "Relatório 3 - Análise de Lucros"]:
                        dados = relatorio.gerar_relatorio(mes_atual, mes_anterior)
                    elif rel_nome == "Relatório 6 - Análise Qualitativa" and analise_text:
                        relatorio.salvar_analise(mes_atual, analise_text)
                        dados = relatorio.gerar_relatorio(mes_atual)
                    else:
                        dados = relatorio.gerar_relatorio(mes_atual)
                    
                    relatorios_dados.append((rel_nome, dados))
                
                pdf_gen = PDFGenerator()
                output_path = f"Relatorio_{cliente_nome.replace(' ', '_')}_{mes_nome}_{ano}.pdf"
                pdf_file = pdf_gen.generate_pdf(relatorios_dados, cliente_nome, mes_nome, ano, output_path)
                
                st.success("Relatório gerado com sucesso!")
                with open(pdf_file, "rb") as f:
                    st.download_button(
                        label="📥 Baixar Relatório PDF",
                        data=f,
                        file_name=output_path,
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Erro ao gerar relatório: {str(e)}")
                st.exception(e)
                st.warning("Certifique-se de que o wkhtmltopdf está instalado e no PATH do sistema.")

if __name__ == "__main__":
    main()