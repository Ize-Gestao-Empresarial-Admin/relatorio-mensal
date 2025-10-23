"""
Entry point simplificado para Streamlit Cloud
"""

import streamlit as st
import sys
import os

# Configuração de path para Streamlit Cloud
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import com tratamento de erro
try:
    from src.interfaces.streamlit_ui import main
    
    # Executar aplicação
    main()
    
except Exception as e:
    st.error("🚨 **ERRO DE CONFIGURAÇÃO DO AMBIENTE**")
    st.write("Problema detectado na configuração dos módulos Python.")
    st.code(f"Erro: {str(e)}")
    
    # Debug info
    with st.expander("Informações de Debug"):
        st.write("**Diretório atual:**", current_dir)
        st.write("**Python path:**", sys.path[:5])
        st.write("**Arquivos na raiz:**", os.listdir(current_dir) if os.path.exists(current_dir) else "N/A")
        if os.path.exists("src"):
            st.write("**Arquivos em src/:**", os.listdir("src"))
        
    st.warning("Entre em contato com o suporte técnico.")