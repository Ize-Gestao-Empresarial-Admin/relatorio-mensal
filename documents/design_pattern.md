# Arquitetura do Sistema de Relatórios Mensais

## Explicação da Arquitetura

O sistema segue o **Padrão de Arquitetura em Camadas (Layered Architecture)**, organizando o código em camadas com responsabilidades bem definidas. Essa estrutura facilita a separação de preocupações, escalabilidade e manutenção, alinhando-se ao **Princípio da Responsabilidade Única (SRP)** do SOLID.

### Estrutura de Camadas

1. **Camada de Dados (Data Layer)**  
   - **Localização**: database  
   - **Arquivos**: `db_utils.py`  
   - **Responsabilidade**: Gerenciar a conexão com o banco de dados e executar consultas SQL.  
   - **Exemplo**: `DatabaseConnection` abstrai o acesso ao banco, retornando resultados para processamento.

2. **Camada de Domínio/Negócio (Business Logic Layer)**  
   - **Localização**: core  
   - **Arquivos**: `indicadores.py`, módulos em `relatorios/`  
   - **Responsabilidade**: Implementar a lógica de negócio principal, como cálculos financeiros e geração de relatórios.  
   - **Exemplo**:
     - `Indicadores`: Calcula valores a partir do banco (ex.: `calcular_custos_variaveis_fc`, `calcular_lucro_bruto_fc`).  
     - `Relatorios`: Classes especializadas (ex.: `Relatorio1`-`Relatorio8`) que geram cada tipo de relatório financeiro.

3. **Camada de Apresentação (Presentation Layer)**  
   - **Localização**: `templates/`, `api.py`
   - **Responsabilidade**: Formatar e apresentar dados ao usuário, seja via API ou templates HTML.
   - **Exemplo**:
     - Templates HTML para cada tipo de relatório organizados por pasta (ex.: `relatorio1/template.html`)
     - API REST para acesso aos relatórios via endpoints

4. **Configuração**  
   - **Localização**: Arquivos .env, config  
   - **Responsabilidade**: Centralizar configurações do sistema.

### Recursos Estáticos

- **Localização**: assets
- **Responsabilidade**: Armazenar arquivos estáticos como imagens, ícones e estilos.
- **Exemplo**: Logos, ícones e imagens de fundo para os relatórios.

### Princípios e Padrões Adicionais

- **Separação de Responsabilidades**:
  - Cada módulo tem uma responsabilidade específica, como geração de um tipo específico de relatório.

- **Injeção de Dependências**:
  - As classes de relatório recebem `Indicadores` e outros parâmetros via construtor (ex.: `Relatorio1(indicadores, nome_cliente)`).

- **Modularidade**:
  - Cada tipo de relatório é uma classe independente, permitindo desenvolvimento e testes isolados.

### Fluxo de Dados

1. O cliente faz uma requisição ao sistema via Streamlit (em breve API através dos endpoints em api.py).
2. O Streamlit faz a chamada das classes específicas de relatório (ex.: `Relatorio1`, `Relatorio2`) do pacote `src.core.relatorios`.
3. Essas classes dependem dos `Indicadores` para obter os dados financeiros.
4. `Indicadores` consulta o banco via `DatabaseConnection`.
5. Os resultados são processados, formatados e retornados como JSON ou incorporados em templates HTML para gerar PDFs.

### Estrutura Real do Diretório

```
.
├── .env                    # Configurações de ambiente
├── .gitignore              # Arquivos ignorados pelo Git
├── api.py                  # API REST para acesso aos relatórios
├── frontend.md             # Documentação da estrutura do frontend
├── main.py                 # Ponto de entrada da aplicação
├── packages.txt            # Dependências do sistema
├── pytest.ini              # Configuração de testes
├── README.md               # Documentação geral do projeto
├── requirements.txt        # Dependências Python
├── saidas.txt              # Log de saídas dos testes
├── test_relatorio_1.py     # Testes para Relatório 1
├── test_relatorio_2.py     # Testes para Relatório 2
├── ...                     # Outros testes de relatórios
├── .devcontainer/          # Configuração do ambiente de desenvolvimento
├── .streamlit/             # Configuração do Streamlit (se utilizado)
├── .vscode/                # Configuração do VS Code
├── assets/                 # Arquivos estáticos (imagens, ícones)
├── config/                 # Configurações do sistema
├── documents/              # Documentação adicional
│   ├── api.md              # Documentação da API
│   ├── design_pattern.md   # Padrões de design
│   └── nova_interface.md   # Especificação da nova interface
├── outputs/                # PDFs e outros arquivos gerados
├── src/
│   ├── core/
│   │   ├── indicadores.py  # Lógica de cálculos financeiros
│   │   └── relatorios/     # Classes dos diferentes tipos de relatórios
│   │       ├── relatorio_1.py
│   │       ├── relatorio_2.py
│   │       ├── ...
│   │       └── relatorio_8.py
│   ├── database/           # Camada de acesso a dados
│   └── interfaces/         # Interfaces com o usuário
└── templates/              # Templates HTML para renderização dos relatórios
    ├── base/               # Templates base (cabeçalho, rodapé)
    ├── relatorio1/
    ├── relatorio2/
    ├── ...
    └── relatorio8/
```

### Tipos de Relatórios

O sistema implementa oito tipos diferentes de relatórios financeiros:

1. **Relatório 1**: Análise de Fluxo de Caixa (Receitas e Custos Variáveis)
2. **Relatório 2**: Análise de Fluxo de Caixa (Lucro Bruto e Despesas Fixas)
3. **Relatório 3**: Análise de Fluxo de Caixa (Lucro Operacional e Investimentos)
4. **Relatório 4**: Análise de Fluxo de Caixa (Lucro Líquido e Entradas Não Operacionais)
5. **Relatório 5**: Fechamento de Análise de Fluxo de Caixa (Saídas Não Operacionais e Geração de Caixa)
6. **Relatório 6**: Análise por Competência - DRE
7. **Relatório 7**: Indicadores 
8. **Relatório 8**: Parecer Técnico (Nota do Consultor)

Cada relatório tem seu próprio template HTML em `/templates/relatorio{n}/` e sua implementação em `/src/core/relatorios/relatorio_{n}.py`.

### API REST

O sistema oferece uma API REST (api.py) com os seguintes endpoints principais:

- **`/clientes`**: Lista todos os clientes disponíveis
- **`/meses`**: Retorna a lista de meses para seleção
- **`/relatorio/{tipo}/{id_cliente}/{mes}/{ano}`**: Gera um relatório específico (tipo 1-8)
- **`/analise/{id_cliente}/{mes}/{ano}`**: Gerencia análises qualitativas (GET, POST, DELETE)
- **`/gerar-pdf`**: Gera um PDF combinando múltiplos relatórios
- **`/health`**: Verifica a saúde da API

A API utiliza FastAPI e implementa validação de dados com Pydantic para garantir a integridade das entradas.

### Benefícios da Arquitetura

- **Manutenção**: Alterações em uma camada (como a interface ou o banco de dados) têm impacto mínimo nas outras.
- **Testabilidade**: Os testes unitários (`test_relatorio_*.py`) podem verificar cada relatório individualmente.
- **Reutilização**: A lógica de negócio das classes de relatório pode ser usada tanto pela API quanto por outras interfaces.
- **Extensibilidade**: Novos tipos de relatórios podem ser adicionados seguindo o mesmo padrão.

Esta arquitetura em camadas proporciona uma base sólida para o sistema de Relatórios Mensais, permitindo seu crescimento e adaptação às necessidades do negócio de forma sustentável.