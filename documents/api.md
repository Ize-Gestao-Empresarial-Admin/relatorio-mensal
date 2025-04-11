# Documentação da API de Relatórios Financeiros

## Introdução

Este documento explica como foi elaborada a API para o sistema de relatórios financeiros, suas características, decisões de design e como trabalhar com ela. Este guia é direcionado para desenvolvedores iniciantes que precisam entender, manter ou estender a API.

## Por que criamos esta API?

O sistema de relatórios financeiros precisava de uma camada de serviço que:

1. **Separasse a lógica de negócio da interface** - Permitindo que diferentes interfaces (web, mobile, desktop) possam consumir os mesmos dados
2. **Documentasse automaticamente os endpoints** - Facilitando o entendimento e uso da API
3. **Padronizasse o acesso aos relatórios** - Criando um fluxo consistente para todos os tipos de relatórios
4. **Permitisse escalabilidade** - Possibilitando adicionar novos tipos de relatórios sem reescrever o sistema

Antes, o código estava acoplado à interface Streamlit, o que tornava difícil reutilizá-lo em outros contextos ou escalar o sistema.

## Tecnologias escolhidas

### FastAPI

Escolhemos o FastAPI pelos seguintes motivos:

- **Performance**: É um dos frameworks Python mais rápidos para APIs
- **Documentação automática**: Gera Swagger e ReDoc automaticamente
- **Validação automática**: Integração com Pydantic para validação de dados
- **Tipagem**: Suporte a type hints para melhor documentação e autocompletar
- **Simplicidade**: Sintaxe declarativa e intuitiva

### Pydantic

Usamos Pydantic para definir os modelos de dados porque:

- Valida os dados de entrada automaticamente
- Gera documentação para os modelos de dados
- Permite conversões automáticas entre tipos
- Integra-se perfeitamente com o FastAPI

## Estrutura da API

A API foi organizada em torno de recursos principais:

1. **Clientes** - Listagem de clientes disponíveis
2. **Relatórios** - Endpoints para gerar diferentes tipos de relatórios
3. **Análises** - Endpoints para gerenciar análises qualitativas
4. **PDF** - Endpoint para geração de relatórios em PDF

## Endpoints principais e suas funções

### Listagem de dados básicos

- `/clientes` - Retorna todos os clientes disponíveis
- `/meses` - Retorna a lista de meses para seleção

### Relatórios individuais

- `/relatorio/{tipo}/{id_cliente}/{mes}/{ano}` - Gera um relatório específico (tipo 1-7)

### Gerenciamento de análises qualitativas

- `GET /analise/{id_cliente}/{mes}/{ano}` - Obtém a análise qualitativa
- `POST /analise/{id_cliente}/{mes}/{ano}` - Salva uma nova análise qualitativa
- `DELETE /analise/{id_cliente}/{mes}/{ano}` - Remove uma análise qualitativa

### Geração de PDF

- `POST /gerar-pdf` - Gera um PDF combinando múltiplos relatórios

### Monitoramento

- `/health` - Verifica a saúde da API

## Como foi implementada a API

### 1. Modelos de dados

Começamos definindo os modelos de dados com Pydantic:

```python
class AnaliseInput(BaseModel):
    analise: str

class RelatorioQuery(BaseModel):
    id_cliente: int
    mes: int 
    ano: int
    mes_anterior: Optional[bool] = True

class RelatorioPdfInput(BaseModel):
    id_cliente: int
    mes: int
    ano: int
    nome_cliente: str
    relatorios: List[int] = [1, 2, 3, 4, 5, 6, 7]
    analise_qualitativa: Optional[str] = None
```

Estes modelos garantem que os dados recebidos pela API sejam validados automaticamente.

### 2. Reutilização de código existente

Em vez de reescrever a lógica de negócios, conectamos a API às classes já existentes:

```python
from src.core.indicadores import Indicadores
from src.core.relatorios.relatorio_1 import Relatorio1
# ... outros imports
from src.database.db_utils import DatabaseConnection, buscar_clientes, obter_meses
from src.interfaces.pdf_generator import PDFGenerator
```

### 3. Injeção de dependências

Criamos um sistema de injeção de dependências para facilitar os testes:

```python
def get_db():
    db = DatabaseConnection()
    return db

@app.get("/clientes")
def listar_clientes(db: DatabaseConnection = Depends(get_db)):
    # ...
```

### 4. Documentação extensiva

Cada endpoint foi documentado com:

- **Summary**: Resumo curto da funcionalidade
- **Description**: Descrição detalhada
- **Docstring**: Explicação dos parâmetros e retornos
- **Tipos**: Anotações de tipo para todos os parâmetros e retornos

Isso garante que a documentação automática gerada pelo FastAPI seja completa e útil.

### 5. Tratamento de erros

Implementamos tratamento de erros consistente:

```python
if tipo < 1 or tipo > 7:
    raise HTTPException(status_code=400, detail="Tipo de relatório inválido (deve ser 1-7)")

cliente = next((c for c in clientes if c["id_cliente"] == id_cliente), None)
if not cliente:
    raise HTTPException(status_code=404, detail="Cliente não encontrado")

try:
    # código
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(e)}")
```

## Como estender a API

### Adicionando um novo endpoint

Para adicionar um novo endpoint:

1. **Defina o modelo de dados** (se necessário):

    ```python
    class NovoModelo(BaseModel):
        campo1: str
        campo2: int
    ```

2. **Crie a função do endpoint**:

    ```python
    @app.get("/novo-endpoint", 
            response_model=Dict[str, Any],
            summary="Descrição curta",
            description="Descrição detalhada")
    def novo_endpoint(parametro: str, db: DatabaseConnection = Depends(get_db)):
        """Docstring explicando o endpoint."""
        # Implementação
        return {"resultado": "valor"}
    ```

### Adicionando um novo tipo de relatório

Se um novo tipo de relatório (8) for criado:

1. Crie a classe `Relatorio8` na estrutura de pasta correta
2. Adicione o import no início do arquivo
3. Adicione a classe ao dicionário de mapeamento:

    ```python
    relatorio_classes = {
        # ... classes existentes
        8: Relatorio8
    }
    ```

4. Adicione o nome do relatório no dicionário de nomes:

    ```python
    rel_nome = f"Relatório {rel_tipo} - " + {
        # ... nomes existentes
        8: "Nome do Novo Relatório"
    }[rel_tipo]
    ```

## Por onde começar a entender esta API

1. **Examine a documentação Swagger**: Acesse `/docs` quando a API estiver rodando
2. **Entenda os modelos de dados**: Analise as classes `BaseModel` no início do código
3. **Estude os endpoints principais**: Comece com `/relatorio/{tipo}/{id_cliente}/{mes}/{ano}` e `/gerar-pdf`
4. **Veja os fluxos de uso comum**: Como listar clientes → obter relatório → gerar PDF

## Como executar a API

Para iniciar a API em modo de desenvolvimento:

```bash
python api.py
```

Para produção, recomendamos usar um servidor ASGI como o uvicorn com workers:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

## Valor gerado para o sistema

Esta API:

1. **Aumenta a reutilização de código**: A lógica de negócios pode ser acessada por qualquer interface
2. **Melhora a documentação**: O Swagger automático documenta todos os endpoints
3. **Facilita a integração**: Sistemas externos podem consumir os dados facilmente
4. **Permite escalabilidade**: Novos relatórios e funcionalidades podem ser adicionados sem impactar o existente
5. **Possibilita monitoramento**: Endpoints de health check facilitam o monitoramento

## Conclusão

Esta API foi projetada pensando em escalabilidade, manutenção e facilidade de uso. Seguindo os princípios de design RESTful e aproveitando os recursos do FastAPI, criamos uma interface robusta e bem documentada para o sistema de relatórios financeiros.

Lembre-se de que o código é vivo e deve evoluir com as necessidades do negócio. A documentação automática ajudará novos desenvolvedores a entenderem e contribuírem para o projeto.
