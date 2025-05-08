import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

class Graficos:
    def __init__(self, static_dir: str):
        self.static_dir = static_dir

    def grafico_r1(self, dados, empresa, mes, ano):
        """Gera um gráfico de colunas com as principais categorias de Receitas e Custos Variáveis."""
        # Extrair categorias e totais do dicionário
        categorias = []
        valores = []
        pesos = []
        avs = []
        ahs = []

        # Total de receitas e custos para calcular pesos
        total_receita = dados.get("Receita", 0)
        total_custos = abs(dados.get("Custos Variáveis", 0))  # Absoluto para pesos

        # Processar Receitas (até 5 categorias)
        for i in range(1, 6):
            categoria = dados.get(f"categoria_peso_{i}_receita")
            total = dados.get(f"total_{i}_receita", 0)
            if categoria and total > 0:
                peso = (total / total_receita * 100) if total_receita > 0 else 0
                av = peso  # AV é o mesmo que peso para receitas (proporção do total)
                # AH requer comparação com mês anterior, mas não temos os dados do mês anterior para categorias
                ah = 0  # Simplificação, já que mes_anterior não é passado
                categorias.append(f"{categoria} (Receita)")
                valores.append(total)
                pesos.append(round(peso, 2))
                avs.append(round(av, 2))
                ahs.append(round(ah, 2))

        # Processar Custos Variáveis (até 5 categorias)
        for i in range(1, 6):
            categoria = dados.get(f"categoria_peso_{i}_custo")
            total = dados.get(f"total_{i}_custo", 0)
            if categoria and total < 0:
                peso = (abs(total) / total_custos * 100) if total_custos > 0 else 0
                av = (total / total_receita * 100) if total_receita > 0 else 0  # AV em relação à receita
                ah = 0  # Simplificação, já que mes_anterior não é passado
                categorias.append(f"{categoria} (Custo)")
                valores.append(abs(total))  # Usar absoluto para o gráfico
                pesos.append(round(peso, 2))
                avs.append(round(av, 2))
                ahs.append(round(ah, 2))

        # Criar DataFrame
        df = pd.DataFrame({
            "Categoria": categorias,
            "Valor": valores,
            "Peso (%)": pesos,
            "AV (%)": avs,
            "AH (%)": ahs
        })

        # Gerar gráfico
        plt.figure(figsize=(12, 6))
        sns.barplot(data=df, x="Categoria", y="Valor", hue="Categoria", palette="viridis")
        plt.title(f"Principais Categorias - {empresa} - {mes}/{ano}")
        plt.xlabel("Categorias")
        plt.ylabel("Valores (R$)")
        plt.grid(True)

        # Adicionar valores nas barras
        for index, row in df.iterrows():
            plt.text(index, row["Valor"], f"R$ {row['Valor']:,.2f}", color='black', ha="center", va="bottom")

        # Criar legenda personalizada
        legend_labels = [
            f"{row['Categoria']}: Peso={row['Peso (%)']}%, AV={row['AV (%)']}%, AH={row['AH (%)']}%"
            for _, row in df.iterrows()
        ]
        plt.legend(labels=legend_labels, title="Detalhes", bbox_to_anchor=(1.05, 1), loc='upper left')

        # Ajustar layout para evitar corte
        plt.tight_layout()

        # Salvar gráfico
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