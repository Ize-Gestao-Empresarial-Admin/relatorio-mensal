# src/core/relatorios/relatorio_6.py
from datetime import date
import json
import os
import streamlit as st

class Relatorio6:
    def __init__(self, indicadores, nome_cliente: str):
        self.indicadores = indicadores
        self.nome_cliente = nome_cliente
        self.id_cliente = indicadores.id_cliente
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..", "data", "analises"))
        os.makedirs(self.base_dir, exist_ok=True)
        print(f"Diretório base: {self.base_dir}")

    def _get_file_path(self, mes_atual: date) -> str:
        data_str = mes_atual.strftime("%Y-%m")
        file_path = os.path.join(self.base_dir, f"analise_{self.id_cliente}_{data_str}.json")
        print(f"Caminho do arquivo: {file_path}")
        return file_path

    @st.cache_data
    def gerar_relatorio(_self, mes_atual: date) -> dict:
        """Gera o relatório 6 com dados existentes ou vazios (com cache)."""
        file_path = _self._get_file_path(mes_atual)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "Empresa": _self.nome_cliente,
            "Data": mes_atual.strftime("%Y-%m-%d"),
            "Analise": ""
        }

    def salvar_analise(self, mes_atual: date, analise: str):
        """Salva a análise em um arquivo JSON."""
        file_path = self._get_file_path(mes_atual)
        relatorio = {
            "Empresa": self.nome_cliente,
            "Data": mes_atual.strftime("%Y-%m-%d"),
            "Analise": analise
        }
        try:
            print("Tentando salvar análise...")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(relatorio, f, ensure_ascii=False, indent=4)
            print(f"Análise salva em: {file_path}")
            self.gerar_relatorio.clear()  # Limpa o cache
        except Exception as e:
            print(f"Erro ao salvar análise: {e}")
            raise

    def excluir_analise(self, mes_atual: date):
        """Exclui o arquivo JSON da análise."""
        file_path = self._get_file_path(mes_atual)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Análise excluída: {file_path}")
            self.gerar_relatorio.clear()  # Limpa o cache