# Arquitetura do Sistema de Relatórios Mensais

## Explicação da Arquitetura

O sistema segue o **Padrão de Arquitetura em Camadas (Layered Architecture)**, organizando o código em camadas distintas com responsabilidades bem definidas. Esse padrão facilita a separação de preocupações, escalabilidade e manutenção, alinhando-se ao **Princípio da Responsabilidade Única (SRP)** do SOLID.

### Estrutura de Camadas

1. **Camada de Dados (Data Layer)**  
   - **Localização**: `src/database/`  
   - **Arquivos**: `db_utils.py`  
   - **Responsabilidade**: Gerenciar a conexão com o banco de dados e executar consultas SQL.  
   - **Exemplo**: `DatabaseConnection` abstrai o acesso ao PostgreSQL, retornando resultados como DataFrames do Pandas.

2. **Camada de Domínio/Negócio (Business Logic Layer)**  
   - **Localização**: `src/core/`  
   - **Arquivos**: `indicadores.py`, `relatorios.py`, `analises.py`  
   - **Responsabilidade**: Implementar a lógica de negócio principal, como cálculos financeiros, geração de relatórios e análises.  
   - **Exemplo**:
     - `Indicadores`: Calcula valores a partir do banco (ex.: `calcular_dre`, `calcular_nivel_1`).  
     - `Relatorios`: Gera relatórios completos (ex.: `gerar_relatorio_1`, `gerar_relatorio_2`).  
     - `AnalisesFinanceiras`: Fornece métodos de análise (ex.: `calcular_analise_vertical`).

3. **Camada de Apresentação (Presentation Layer)**  
   - **Localização**: `src/interfaces/`  
   - **Arquivos**: `streamlit_ui.py`, `graficos.py`  
   - **Responsabilidade**: Exibir dados ao usuário e gerenciar interações visuais.  
   - **Exemplo**:
     - `streamlit_ui.py`: Interface Streamlit para selecionar empresas/meses e mostrar relatórios.  
     - `graficos.py`: Gera gráficos Plotly (ex.: `grafico_r1`, `grafico_r2`).

4. **Configuração (Configuration Layer)**  
   - **Localização**: `config/`  
   - **Arquivos**: `settings.py`  
   - **Responsabilidade**: Centralizar configurações do sistema, como credenciais do banco.  
   - **Exemplo**: `DB_CONFIG` define parâmetros de conexão ao PostgreSQL.

### Recursos Estáticos

- **Localização**: `static/`
- **Responsabilidade**: Armazenar arquivos estáticos como imagens, ícones e estilos usados pela Camada de Apresentação.
- **Exemplo**:
  - `assets/images/logo.png`: Logo exibido na interface.
  - `assets/images/relatorio_7_p1.png`: Imagem comercial IZE Relatório 7.

### Princípios e Padrões Adicionais

- **Separação de Responsabilidades (SRP - Single Responsibility Principle)**:
  - Cada módulo tem uma única responsabilidade clara, reduzindo acoplamento e facilitando testes.

- **Injeção de Dependências (Dependency Injection)**:
  - Dependências como `DatabaseConnection` e `Indicadores` são injetadas via construtores, permitindo substituição por mocks em testes (ex.: `Relatorios(indicadores, nome_cliente)`).

- **Modularidade**:
  - Cada arquivo é independente e pode ser testado ou expandido separadamente, como adicionar novos relatórios ou indicadores.

### Escalabilidade para API

- A lógica de negócio em `core` é reutilizável para uma futura API.
- Um arquivo `api.py` (a ser criado com FastAPI ou Flask) pode consumir `Relatorios` e `Indicadores` diretamente, mantendo a mesma estrutura.

### Configuração Centralizada

- `config/settings.py` centraliza configurações (ex.: conexão ao banco), evitando duplicação e facilitando ajustes globais.

### Fluxo de Dados

1. O usuário interage com `streamlit_ui.py` (Camada de Apresentação).
2. `streamlit_ui.py` instancia as classes específicas de relatório (como `Relatorio1`, `Relatorio2`, etc.) importadas do pacote `src.core.relatorios`. Cada uma dessas classes de relatório depende de `Indicadores` (Camada de Negócio).
3. `Indicadores` consulta o banco via `DatabaseConnection` (Camada de Dados).
4. Os resultados são processados em `core` e retornados para visualização em `interfaces`.

### Benefícios

- **Manutenção**: Alterações em uma camada (ex.: mudar o banco) não afetam as outras.
- **Testabilidade**: Camadas isoladas permitem testes unitários com mocks (ex.: `pytest` com `unittest.mock`).
- **Reutilização**: A lógica de `core` pode ser usada em diferentes interfaces (Streamlit, API, CLI).

### Estrutura de Diretórios

``` python
arq_relatorio_mensal/
├── static/                 # Diretório para recursos estáticos
│   ├── images/             # Subdiretório para imagens
│   │   ├── logo.png        # Logo da empresa 
│   │   ├── relatorio_7_p1.png  # Ícone para cards
│   │   └── relatorio_7_p2.png  # Fundo para relatórios
│   └── icons/             # Subdiretório para ícones
│       └── icon_ize.png   # Ícone da empresa
├── config/
│   └── settings.py         # Configurações centralizadas
├── data/
│   └── analises/           # Diretório para arquivos JSON
│       ├── analise_105_2025-01.json #Exemplo de relatórios do consultor contendo id_cliente e data no nome.
├── src/
│   ├── core/
│   │   ├── indicadores.py  # Cálculos financeiros
│   │   ├── relatorios/
│   │   |   ├── __init__.py # Importa e expõe as classes de relatórios disponíveis na aplicação.
│   │   │   ├── relatorio_1.py # Relatório tipo 1
│   │   │   ├── relatorio_2.py # Relatório tipo 2
│   │   │   ├── relatorio_3.py # Relatório tipo 3
│   │   │   ├── relatorio_4.py # Relatório tipo 4
│   │   │   ├── relatorio_5.py # Relatório tipo 5
│   │   │   ├── relatorio_6.py # Relatório tipo 6
│   │   │   └── relatorio_7.py # Relatório tipo 7
│   │   └── analises.py     # Análises financeiras (AV, AH)
│   ├── database/
│   │   └── db_utils.py     # Conexão e consultas ao banco
│   ├── interfaces/
│   │   ├── streamlit_ui.py # Interface Streamlit
│   │   ├── graficos.py     # Geração de gráficos
|   |   └── components.py   # Componentes reutilizáveis do Streamlit
│   └── models/             # (Futuro) Estruturas de dados
├── tests/
│   ├── test_indicadores.py # Testes unitários para indicadores
│   ├── test_relatorios.py  # Testes unitários para relatórios
│   └── test_analises.py    # Testes unitários para análises
├── main.py                 # Ponto de entrada do Streamlit
├── design_pattern.md      # Documentação da arquitetura e padrões de design do sistema
└── README.md              # Documentação geral
```
