# Projeto Relatório Mensal

## Objetivo

Este projeto visa automatizar o envio de relatórios financeiros mensais, organizando documentação e processos de colaboração. O foco é proporcionar um design profissional, com gráficos interativos e exportação em PDF, garantindo também a escalabilidade e personalização fina pelo consultor.

**Exemplo base de relatório** (feito manualmente por um consultor no Canva):
<https://www.canva.com/design/DAGfZdH3Yp4/gtgxavirhcMGSjwGepvNYA/edit?utm_content=DAGfZdH3Yp4&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton>

## Funcionalidades Principais

- **Automatização**: Envio automático de relatórios.
- **Entrega Prioritária**: Disponível até o dia 05 do mês.
- **Gráficos em Todas as Páginas**: Visualização interativa para melhor análise.
- **Escalabilidade**: Adaptável para futuras alterações.
- **Personalização Fina**: Ajustes feitos pelo consultor.
- **Notas Automatizadas**: Notas com texto padrão, mudando apenas o dado.
- **Parecer Técnico** (Opcional): Inclusão de análise técnica na página final.
- **Mensagem Padrão**: Caso o relatório não esteja disponível, exibir aviso.
- **Formato Flexível**: Apresentação como página web com opção de exportação
- **Identidade Visual**: Respeitar a identidade padrão da empresa. Revisão e aprovação por Kaio Augusto.

## Estrutura do Relatório

### Capa do Relatório - Página 0.5

Capa padrão do relatório mensal (olhar os arquivos de design para identidade de cores da marca)

### Página 1 - Análise do Fluxo de Caixa

- **Componente Gráfico** de colunas com legenda:
  - Receita
  - Custo Variável
  - Despesa Fixa
  - Investimentos
- **Indicadores principais**:
  - Receita
  - Custo Variável
  - Despesa Fixa
  - Lucro Operacional
  - Análise vertical (só das despesas e do lucro)
  - Análise horizontal (Variação)
- **Notas Automatizadas**: Inclui análise automática dos dados apresentados.
- **Mensagem Padrão**: Se não houver dados, exibir aviso.
- **Observação**: Dados podem ser extraídos do B.I. ou Banco de Dados SQL.

### Página 2 - Análise por Competência - DRE

- **Componente Gráfico** incluindo:
  - Faturamento
  - Dedutíveis (dedução)
  - Variável
  - Despesas fixas
- **Indicadores Principais**:
  - Faturamento
  - Custo variável + dedução da receita
  - Custo com Produto e Serviço
  - Despesa fixa
  - EBITDA
  - Lucro Operacional
  - Lucro Líquido
  - Cálculo de: Valor + representatividade.
- **Notas automatizadas**: Inclui análise automática dos dados apresentados.

### Página 3 - Análise de Lucros

- **Componente Gráfico Comparativo** em camadas:
  - Formato de colunas em camadas.
  - Comparativo com Ponto de equilíbrio + Lucro Operacional - sempre dos ultimos 3 meses fechados.
- **Indicadores principais**:
  - Lucro Bruto
  - Lucro Operacional
  - Lucro Líquido
  - Geração de Caixa
  - Análise de Representatividade (Vertical) (%)
  - Análise Horizontal (Variação)
- **Notas automatizadas**: Inclui análise automática dos dados apresentados.

### Página 4 - Evolução - Comparativo da Receita e Geração de Caixa

- **Componente Gráfico de Linha**:
  - Percentual da Receita (comparativo de 3 meses + média das receitas dos 3 meses)
  - Lucro Operacional (%)
  - Linha tracejada para média do valor (lucro e receita)
  - Tags de valor como base comparativa do resultado
  - Dados limitados a 3 meses (entrada e saída dinâmica)
- **Componente Gráfico de linha do Caixa Acumulado**:
  - Comparativo de 3 meses
  - Linha de média da geração de caixa
  - Cálculo da soma das 3 gerações de caixa (acumulado)

### Página 5 - Indicadores

- **Indicadores Principais**:
  - Página de indicadores igual ao dashboard do cliente (power B.I.) na vertical.
  - 16 indicadores (padrão)
  - Ticket Médio, CAC, LTV, M.C%, Indicador Crescimento, Crescimento Ano Anterior, P.E, P.E +15%, NCG, PME, PMR, PMP, Caixa Mínimo, Saldo, Indicador Caixa, Investimentos
  - Nome do indicador no BD: "Ticket Médio", "CAC", "LTV", "M.C %", "Indicador Crescimento", "Crescimento Ano Anterior", "P.E", "P.E+15%", "NCG", "PME", "PMR", "PMP", "Caixa Mínimo", "Saldo", "Indicador Caixa", "% Investimentos".

### Página 6 (Opcional) - Parecer Técnico

- Criado manualmente pelo consultor para cada cliente.
- Análise geral de conclusão do relatório.

### Página 7 (última página) - Marketing e Propaganda

- Canais de comunicação da IZE.

## Próximos Passos

1. **Definição das tecnologias**:
     - Backend: Python com arquitetura em camadas e SRP, API com FastAPI
     - Frontend e Visualização de dados: Streamlit ou Plotly
     - Banco de Dados: PostgreSQL
     - Infraestrutura: Docker para escalabilidade
2. **Desenvolvimento do Protótipo**: Criar versão inicial para testes.
3. **Ajustes conforme feedback**.
4. **Lançamento Oficial**: Implementação para os consultores

**Link do briefing original (notion)**: [Briefing Inicial do Projeto](https://www.notion.so/Briefing-Inicial-do-Projeto-19f1c5585bdc80e6b253e786bb347082?pvs=4)
