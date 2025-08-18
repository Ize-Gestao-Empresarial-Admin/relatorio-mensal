<!-- markdownlint-disable MD036 -->

# API de Relatórios Mensais IZE (FastAPI)

## 1) Visão geral

A API expõe os mesmos fluxos e regras do app Streamlit (`src/interfaces/streamlit_ui.py`)para gerar relatórios financeiros (1 a 8) e consolidá-los em um PDF. Público-alvo desta documentação: devs que vão **entender, manter e estender** a API e o projeto.

**Principais blocos do sistema:**

- **FastAPI**: camada HTTP + OpenAPI/Swagger.
- **Pydantic**: validação de entrada/saída.
- **Core de negócio** (`src/core/...`): `Indicadores.py` e `relatorios/Relatorio1..8 (.py)`.
- **Camada de dados** (`src/database/db_utils.py` e `config/settings.py`): consultas (clientes, meses, anos) e conexão ao banco de dados (via `.env`).
- **Renderização** (`src/rendering/engine.py` e `src/rendering/renderers/relatorioX_renderer.py`): HTML → PDF (wkhtmltopdf) e diferentes arquivos de rendererização para cada tipo de relatório (a formatação de valores segue o arquivo `base_renderer.py` presente na mesma pasta).

```bash
[Client] → [FastAPI] → [Indicadores / Relatorios] → [RenderingEngine] → PDF (Streaming)
                                   ↑
                              [Database]
```

## 2) Autenticação, autorização e CORS

- **Auth**: API Key via header `X-API-Key`.
  - Servidor lê `API_KEY` do ambiente. Se **não** definido, gera um erro 500 (configuração inválida).
  - **Importante**: em produção, sempre defina `API_KEY` para evitar acesso não autorizado.
- **CORS**: liberado por padrão. **Configure** isso em produção (defina domínios permitidos por segurança).

## 3) Como rodar localmente

### Requisitos

- Ambiente recomendado: `WSL Linux Ubuntu` (maior compatibilidade devido ao arquivo `packages.txt`)
- Python 3.10+
- wkhtmltopdf instalado no sistema
  - Windows: [instalador oficial](https://wkhtmltopdf.org/downloads.html) ou via Chocolatey: `choco install wkhtmltopdf`
  - Debian/Ubuntu: `sudo apt-get install wkhtmltopdf`
  - macOS: `brew install wkhtmltopdf`
- Variáveis de ambiente:
  - `API_KEY=<sua_chave>` (obrigatória)
  - as usadas por `DatabaseConnection` (ex.: host, dbname etc.), que são lidas dentro de `config/settings.py` (obs.: não alterar a chamada de envs do Streamlit, são importantes para o deploy do project pois as keys estão em `.streamlit/secrets.toml`).:

### Instalação & run

```bash
pip install -r requirements.txt
uvicorn src.api.main:app --reload --port 8000

```

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Como autenticar no Swagger:** clique em **Authorize** → informe a API key no campo `X-API-Key`.

## 4) Convenções e versionamento

- Prefixo de versão: `/v1/...`
- Respostas de erro padronizadas (HTTPException do FastAPI):
  - `401` API Key ausente/errada
  - `422` erro de validação (Pydantic)
  - `500` erro interno (ex.: renderização PDF ou API_KEY não configurada)

## 5) Estrutura da API

A API é organizada em torno do modelo principal `RelatorioRequest` que processa os parâmetros de geração de PDF. Características principais:

- **Normalização de parâmetros**: O endpoint aceita flexibilidade no formato dos valores (ex: relatórios podem ser enviados como IDs numéricos, strings, ou combinação)
- **Validação robusta**: Campos são validados tanto em tipo quanto em regras de negócio
- **Índice**: sempre insere o "Índice" como primeira seção do PDF.
- **Multi-cliente**: aceite de múltiplos `cliente_ids` e nome exibido automático derivado do cliente base ou com sufixo "_Consolidado".

## 6) Estrutura do código (API)

Arquivo principal: `src/api/main.py`

- **Segurança**: API key (header `X-API-Key`)
- **Constantes globais**:
  - `RELATORIO_CLASSES`: mapeamento de IDs para classes de relatório
  - `RELATORIO_LABELS`: mapeamento de IDs para nomes de exibição
- **Utilitários**:
  - `processar_html_parecer(html)`: converte classes Quill para CSS inline
  - `slugify_filename(text)`: sanitiza nomes de arquivo
  - `get_mes_numero(mes)`: validação e normalização do mês
  - `default_ano(ano)`: fornece ano atual como default
- **Endpoints**:
  - `GET /v1/health`
  - `GET /v1/clientes`
  - `GET /v1/anos?id_cliente=...`
  - `GET /v1/meta`
  - `POST /v1/relatorios/pdf` *(principal)*
  - `GET /v1/relatorios/pdf` *(teste via query params)*

## 7) Estendendo a API

### 7.1 Novos endpoints

- Siga o padrão:
  - Utilize o prefixo `/v1/`
  - Utilize `response_model` claro (quando aplicável)
  - Tipagem estrita nos parâmetros (Pydantic/Query)
  - `summary`/`description` para Swagger
  - Tratamento de erro com mensagens objetivas
  - Sempre adicione a dependência `Depends(verify_api_key)` para autenticação

## 8) Testes

- Use `fastapi.testclient.TestClient` para testes de integração.
- "Happy path" essencial:
  - `GET /v1/health`
  - `GET /v1/clientes`
  - `GET /v1/anos?id_cliente=...`
  - `POST /v1/relatorios/pdf` com 1 e com N clientes
  - `Relatório 8` com `analise_text` (HTML)
- "Sad path":
  - 401 sem `X-API-Key` correta
  - 422 com payload inválido (mês fora do range, listas vazias, etc.)
  - 500 quando API_KEY não está configurada no ambiente

## 9) Observabilidade & Operação

- **/v1/health** para verificação se a API está funcionando (liveness).
- Logs: delegados ao servidor/app (configure Uvicorn/Gunicorn + logging do projeto).
- Storage:
  - PDFs são gerados na pasta `outputs/` antes do streaming. Garanta **permissão de escrita** e **limpeza** periódica no ambiente.

## 10) Checklist de Onboarding

- [ ]  Instale wkhtmltopdf
- [ ]  Configure variáveis de DB e **API_KEY**
- [ ]  Rode `uvicorn src.api.main:app --reload`
- [ ]  Teste `/docs` e gere um PDF simples
- [ ]  Revise CORS/domínios em prod
- [ ]  Habilite logs e rotação de arquivos de saída (se aplicável)

## Endpoints & Payloads — Referência Rápida

## Autenticação

- **Header**: `X-API-Key: <sua-chave>` (obrigatório)
- Falha se API_KEY não estiver configurada no servidor ou se a chave estiver incorreta

## Tabela de endpoints

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | `/v1/health` | Health check |
| GET | `/v1/clientes` | Lista clientes ativos (`id_cliente`, `nome`) |
| GET | `/v1/anos` | Anos disponíveis para os clientes informados |
| GET | `/v1/meta` | Metadados: meses (nome/número) e IDs de relatórios |
| **POST** | **`/v1/relatorios/pdf`** | **Gera PDF dos relatórios selecionados** |
| GET | `/v1/relatorios/pdf` | Igual ao POST, mas via query params (para testes) |

---

## `/v1/health` — GET

**200** `{ "status": "ok" }`

---

## `/v1/clientes` — GET

**200**

```json
{
  "clientes": [
    { "id_cliente": 10, "nome": "ACME Ltda" },
    { "id_cliente": 20, "nome": "Foo Bar S/A" }
  ]
}

```

---

## `/v1/anos` — GET

**Query**: `cliente_ids=10,20`

**200**

```json
{ "anos": [2025, 2024, 2023] }

```

**422** se `cliente_ids` ausente/ inválido.

---

## `/v1/meta` — GET

**200**

```json
{
  "meses": [
    ["Janeiro", 1], ["Fevereiro", 2], ["Março", 3]
    // ...
  ],
  "relatorios": [
    "Relatório 1","Relatório 2","Relatório 3","Relatório 4",
    "Relatório 5","Relatório 6","Relatório 7","Relatório 8"
  ]
}

```

---

## `/v1/relatorios/pdf` — POST (principal)

Gera e **faz streaming** do PDF unificado (Content-Disposition: attachment).

### Body (`application/json`)

```json
{
  "id_cliente": [85],
  "mes": 7,
  "ano": 2025,
  "relatorios": [1, 2, 3, 4, 5, 6, 7],
  "analise_text": "<p><span class=\\"ql-size-large\\"><strong>Visão Geral:</strong></span> Margem saudável.</p>"
}

```

### Regras importantes

- **Período**:
  - `mes` deve estar entre 1 e 12
  - se ausente → mês **anterior** ao atual
  - `ano` ausente → ano atual
- **Multi-cliente**:
  - `id_cliente` é sempre uma lista (mesmo com um único ID)
  - Se lista tiver mais de um ID, o nome exibido será `"<NomeBase>_Consolidado"`
- **Relatórios**:
  - IDs numéricos (1-8) ou strings com nomes dos relatórios
  - Aceita formatos flexíveis: [1,7,8], ["1","7","8"], ["Relatório 1", "Relatório 7"]
  - `Relatório 8` (parecer) aceita `analise_text` (HTML) e normaliza CSS automaticamente (porém é opcional, caso seja automação o envio do relatório deve-se analisar com os consultores e a líder do time se há a necessidade de um parecer individual do cliente.
- **Saída**: PDF é salvo em outputs e enviado no corpo da resposta (streaming)

### Respostas

- **200**: `application/pdf` (stream)
- **401**: API Key ausente/errada
- **422**: payload inválido (ex.: `mes` fora de 1–12, `relatorios` vazio)
- **500**: erro interno (ex.: falha no wkhtmltopdf ou API_KEY não configurada)

### Exemplos de chamada

**cURL**

```bash
curl -X POST "<http://localhost:8000/v1/relatorios/pdf>" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: $API_KEY" \\
  --data '{
    "id_cliente": [85],
    "mes": 6,
    "ano": 2025,
    "relatorios": [1, 2, 3, 4, 5, 6, 7]
  }' \\
  --output Relatorio_ACME_Junho_2025.pdf
```

**Python (requests)**

```python
import requests

url = "<http://localhost:8000/v1/relatorios/pdf>"
headers = {"X-API-Key": "minha-chave", "Content-Type": "application/json"}
payload = {
    "id_cliente": [85],
    "mes": 7,
    "ano": 2025,
    "relatorios": [1, 2, 3, 4, 5, 6, 7],
    "analise_text": "<p><span class=\\"ql-size-large\\">OK</span></p>"
}

r = requests.post(url, headers=headers, json=payload)
open("Relatorio_Consolidado.pdf", "wb").write(r.content)

```

**JavaScript (fetch)**

```jsx
const res = await fetch("<http://localhost:8000/v1/relatorios/pdf>", {
  method: "POST",
  headers: {
    "X-API-Key": "minha-chave",
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    "id_cliente": [10],
    "relatorios": ["Relatório 6","Relatório 7"]
  })
});
const blob = await res.blob();
const url = URL.createObjectURL(blob);
const a = document.createElement("a");
a.href = url;
a.download = "Relatorio.pdf";
a.click();
URL.revokeObjectURL(url);

```

---

## `/v1/relatorios/pdf` — GET (modo "rápido", via query)

Mesmos comportamentos do POST, mas usando query params. Útil para testar no navegador.

**Exemplo**

``` bash
GET /v1/relatorios/pdf
  ?id_cliente=10,20
  &mes=5
  &ano=2025
  &relatorios=Relatório%206,Relatório%207

```

> Dica: analise_text também pode ser enviado por query, mas para HTML é mais seguro usar POST.

---

## Mapeamento de relatórios

| ID | Classe | Observações de chamada |
| --- | --- | --- |
| Relatório 1–4 | `Relatorio1..4` | `gerar_relatorio(mes_atual, mes_anterior)` |
| Relatório 5 | `Relatorio5` | `gerar_relatorio(mes_atual)` |
| Relatório 6 | `Relatorio6` | `gerar_relatorio(mes_atual)` |
| Relatório 7 | `Relatorio7` | `gerar_relatorio(mes_atual)` |
| Relatório 8 | `Relatorio8` | aceita `salvar_analise(mes_atual, html)` |

---

## Mensagens de erro (amostras)

``` bash
// 401
{ "detail": "Não autenticado: forneça X-API-Key válida." }

// 422 (exemplo de validação)
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body","relatorios"],
      "msg": "Selecione pelo menos um relatório."
    }
  ]
}

// 500
{ "detail": "Configuração inválida: defina API_KEY no ambiente (.env)." }
{ "detail": "Erro ao gerar PDF: <mensagem>" }

```
