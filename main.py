# main.py
# Roda o Streamlit
# FORÇA REBUILD STREAMLIT CLOUD - Fix para problema de módulos em subdiretórios

import sys
import os

# Adicionar diretório atual ao Python path para resolver imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.interfaces.streamlit_ui import main #prod
#from src.interfaces.streamlit_ui_dev import main #dev

if __name__ == "__main__":
    main()