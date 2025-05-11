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

- Capa padrão do relatório mensal (olhar os arquivos de design para identidade de cores da marca)

### Página 1 - Análise do Fluxo de Caixa

- **Componente Gráfico de colunas com legenda:**
  - Receita (principais categorias de Receitas (maior peso %) e suas AV e AH)
  - Custo Variável (categorias com maior peso %, AV e AH)
- **Notas Automatizadas:** Inclui explicação sobre a natureza dos custos variáveis (gastos diretamente associados com a operação da empresa, tendem a acompanhar o movimento das receitas, etc).
- **Mensagem Padrão:** Se não houver dados, exibir aviso.

### Página 2 - Análise do Fluxo de Caixa

- **Componente Gráfico de colunas com legenda:**
  - Lucro Bruto (principais categorias do grupo (maior peso %) com AV e AH)
  - Despesas Fixas (categorias com maior impacto %, AV e AH)
- **Indicadores principais:**
  - Lucro Bruto
  - Despesas Fixas
- **Notas Automatizadas:** Explicação sobre o Lucro Bruto e Despesas Fixas. Colocar um pequeno parágrafo de com mensagem padrão trazendo os destaques, apontando a AV de cara categoria.
- **Mensagem Padrão:** Se não houver dados, exibir aviso.

### Página 3 - Análise de Fluxo de Caixa

- **Componente Gráfico de colunas com legenda:**
  - Lucro operacional
  - Investimentos
- **Notas Automatizadas:** Explicação sobre o Lucro Operacional e Investimentos.
- **Mensagem Padrão:** Se não houver dados, exibir aviso.

### Página 4 - Análise de Fluxo de Caixa

- **Componente Gráfico de colunas com legenda:**
  - Lucro Líquido
  - Entradas não Operacionais
- **Indicadores Principais:**
- **Notas automatizadas:** Inclui análise automática dos dados apresentados.

### Página 5 - Fechamento Análise de Fluxo de Caixa

- **Componente Gráfico de colunas com legenda:**
  - Saídas Não operacionais
  - Geração de Caixa
- **Componente Gráfico de linha do Caixa Acumulado:**
  - Comparativo de 3 meses
  - Linha de média da geração de caixa
  - Cálculo da soma das 3 gerações de caixa (os 3 meses) - acumulado. (Exibe quanto ele conseguiu produzir)

### Página 6 - Análise por Competência - DRE

- **Componente Gráfico incluindo:**
  - Faturamento
  - Dedutíveis (dedução)
  - Variável
  - Despesas fixas
- **Indicadores Principais:**
  - Faturamento
  - Custo variável + dedução da receita
  - Custo com Produto e Serviço
  - Despesa fixa
  - EBITDA
  - Lucro Operacional
  - Lucro Líquido
- **Cálculo de:** Valor + representatividade.
- **Notas automatizadas:** Inclui análise automática dos dados apresentados.

### Página 7 - Indicadores

- **Indicadores Principais:**
  - Página de indicadores seja igual ao de indicadores do dashboard do cliente (power b.i) na vertical.

### Página 8 (Opcional) - Parecer Técnico (Nota do Consultor)

- Criado manualmente pelo consultor para cada cliente.
- Análise geral de conclusão do relatório.

### Página 9 (última página) - Marketing e Propaganda

- Canais de comunicação da IZE.

## Tecnologias Utilizadas

- Python (back-end)
- Jinja 2 (template engine)
