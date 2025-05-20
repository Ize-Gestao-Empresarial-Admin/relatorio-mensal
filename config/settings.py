import os
from dotenv import load_dotenv

# Streamlit pode não estar disponível em ambiente de testes ou scripts standalone
try:
    import streamlit as st
    USE_STREAMLIT = True
except ImportError:
    USE_STREAMLIT = False

# Carrega o .env
load_dotenv()

def get_env_var(key: str) -> str | None:
    """Busca a variável de ambiente com fallback para st.secrets se necessário."""
    value = os.getenv(key)
    
    if value is None and USE_STREAMLIT:
        # Tenta buscar nos secrets
        for section in st.secrets:
            if key in st.secrets[section]:
                return st.secrets[section][key]
    return value

DB_CONFIG = {
    "dbname": get_env_var("DB_NAME"),
    "user": get_env_var("DB_USER"),
    "password": get_env_var("DB_PASSWORD"),
    "host": get_env_var("DB_HOST"),
    "port": get_env_var("DB_PORT"),
}
