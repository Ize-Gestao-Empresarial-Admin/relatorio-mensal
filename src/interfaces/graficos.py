import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

class Graficos:
    def __init__(self, static_dir="static/graficos"):
        self.static_dir = os.path.abspath(static_dir)
        os.makedirs(self.static_dir, exist_ok=True)

    def grafico_r1(self, dados, empresa, mes, ano):
        categorias = ["Receita", "Custos Variáveis", "Despesas Fixas", "Investimentos", "Lucro Operacional"]
        valores = [dados.get(cat, 0) for cat in categorias]
        df = pd.DataFrame({"Categoria": categorias, "Valor": valores})

        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x="Categoria", y="Valor", hue="Categoria", palette="viridis", legend=False)
        plt.title(f"Resultados Mensais - {empresa} - {mes}/{ano}")
        plt.xlabel("Categorias")
        plt.ylabel("Valores (R$)")
        plt.grid(True)
        for index, row in df.iterrows():
            plt.text(index, row["Valor"], f"R$ {row['Valor']:,.2f}", color='black', ha="center")
        output_path = os.path.join(self.static_dir, f"grafico_r1_{empresa}_{mes}_{ano}.png")
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        return output_path

    def grafico_r2(self, dados, empresa, mes, ano):
        categorias = ["Faturamento", "Dedutíveis", "Custo Variável", "Despesa Fixa", "EBITDA", "Lucro Operacional", "Lucro Líquido"]
        valores = [dados.get(cat, 0) for cat in categorias]
        df = pd.DataFrame({"Categoria": categorias, "Valor": valores})

        plt.figure(figsize=(12, 6))
        sns.barplot(data=df, x="Categoria", y="Valor", hue="Categoria", palette="magma", legend=False)
        plt.title(f"Análise por Competência - {empresa} - {mes}/{ano}")
        plt.xlabel("Categorias")
        plt.ylabel("Valores (R$)")
        plt.xticks(rotation=45)
        plt.grid(True)
        for index, row in df.iterrows():
            plt.text(index, row["Valor"], f"R$ {row['Valor']:,.2f}", color='black', ha="center")
        output_path = os.path.join(self.static_dir, f"grafico_r2_{empresa}_{mes}_{ano}.png")
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        return output_path

    def grafico_r3(self, dados, empresa, mes, ano):
        dados_3_meses = dados["Dados 3 Meses"]
        meses = [f"Mês {i+1}" for i in range(3)]
        receitas = dados_3_meses["Receita"]
        lucros_operacionais = dados_3_meses["Lucro Operacional"]
        # Usar "Geração de Caixa" do nível principal, não do "Dados 3 Meses"
        geracao_caixa_atual = dados.get("Geração de Caixa", 0)
        # Como "Geração de Caixa" não está nos 3 meses, usamos apenas o valor atual ou omitimos
        # Aqui, vamos plotar apenas Receita e Lucro Operacional dos 3 meses

        df = pd.DataFrame({
            "Mês": meses,
            "Receita": receitas,
            "Lucro Operacional": lucros_operacionais,
        })

        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df.melt("Mês"), x="Mês", y="value", hue="variable", marker="o")
        plt.title(f"Análise de Lucros - {empresa} - Últimos 3 Meses até {mes}/{ano}")
        plt.ylabel("Valores (R$)")
        plt.grid(True)
        output_path = os.path.join(self.static_dir, f"grafico_r3_{empresa}_{mes}_{ano}.png")
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        return output_path

    def grafico_r4(self, dados, empresa, mes, ano):
        meses = dados["Dados 3 Meses"]["Meses"]
        caixa_acumulado = dados["Caixa Acumulado"]

        df = pd.DataFrame({"Mês": meses, "Caixa Acumulado": caixa_acumulado})

        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df, x="Mês", y="Caixa Acumulado", marker="o", color="blue")
        plt.title(f"Evolução do Caixa Acumulado - {empresa} - Últimos 3 Meses até {mes}/{ano}")
        plt.ylabel("Caixa Acumulado (R$)")
        plt.grid(True)
        for i, v in enumerate(caixa_acumulado):
            plt.text(i, v, f"R$ {v:,.2f}", ha="center")
        output_path = os.path.join(self.static_dir, f"grafico_r4_{empresa}_{mes}_{ano}.png")
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        return output_path