# main.py
# Roda o Streamlit
# FORÇA REBUILD STREAMLIT CLOUD - Fix para problema de módulos em subdiretórios

from src.interfaces.streamlit_ui import main #prod
#from src.interfaces.streamlit_ui_dev import main #dev

if __name__ == "__main__":
    main()