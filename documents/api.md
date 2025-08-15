
# API de Relatórios Mensais IZE (FastAPI)

## 1) Visão geral

A API expõe os mesmos fluxos e regras do app Streamlit (`src/interfaces/streamlit_ui.py`)para gerar relatórios financeiros (1 a 8) e consolidá-los em um PDF.
Público-alvo desta documentação: devs que vão **entender, manter e estender** a API e o projeto.

**Principais blocos do sistema:**

* **FastAPI**: camada HTTP + OpenAPI/Swagger.
* **Pydantic**: validação de entrada/saída.
* **Core de negócio** (`src/core/...`): `Indicadores.py` e `relatorios/Relatorio1..8 (.py)`.
* **Camada de dados** (`src/database/db_utils.py` e `config/settings.py`): consultas (clientes, meses, anos) e conexão ao banco de dados (via `.env`).
* **Renderização** (`src/rendering/engine.py`  e `src/rendering/renderers/relatorioX_renderer.py`): HTML → PDF (wkhtmltopdf) e diferentes arquivos de rendererização para cada tipo de relatório (a formatação de valores segue o arquivo `base_renderer.py` presente na mesma pasta).

``` bash
[Client] → [FastAPI] → [Indicadores / Relatorios] → [RenderingEngine] → PDF (Streaming)
                                   ↑
                              [Database]
```

## 2) Autenticação, autorização e CORS

* **Auth**: API Key via header `X-API-Key`.

  * Servidor lê `API_KEY` do ambiente. Se **não** definido, **libera** acesso (modo dev), mas **não recomendado** em produção.
  * **Importante**: em produção, sempre defina `API_KEY` para evitar acesso não autorizado e posteriormente implemente autenticação real (JWT/OAuth).
* **Autorização** (regra atual, alinhada à UI): payload precisa ter `is_admin=True` **ou** `is_consultant=True`.

  > Observação: hoje essa permissão é “confiança do cliente”. Em produção, substitua por **autenticação real** (JWT/OAuth).
* **CORS**: liberado para `*` por padrão. **Configure** isso em prod (defina domínios permitidos por segurança).

## 3) Como rodar localmente

### Requisitos

* Ambiente recomendado: `WSL Linux Ubuntu` (maior compatibilidade devido ao arquivo `packages.txt`)
* Python 3.10+
* wkhtmltopdf instalado no sistema
  * Windows: [instalador oficial](https://wkhtmltopdf.org/downloads.html) ou via Chocolatey: `choco install wkhtmltopdf`
  * Debian/Ubuntu: `sudo apt-get install wkhtmltopdf`
  * macOS: `brew install wkhtmltopdf`

* Variáveis de ambiente:

  * `API_KEY=<sua_chave>` (opcional em dev)
  * as usadas por `DatabaseConnection` (ex.: host, dbname etc.), que são lidas dentro de `config/settings.py` (obs.: não alterar a chamada de envs do Streamlit, são importantes para o deploy do project pois as keys estão em `.streamlit/secrets.toml`).:


### Instalação & run

```bash
pip install -r requirements.txt
uvicorn src.api.main:app --reload --port 8000
```

* Swagger: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

**Como autenticar no Swagger:** clique em **Authorize** → informe a API key no campo `X-API-Key`.

## 4) Convenções e versionamento

* Prefixo de versão: `/v1/...`
* Respostas de erro padronizadas (HTTPException do FastAPI):

  * `401` API Key ausente/errada
  * `403` sem permissão (não é admin/consultant)
  * `422` erro de validação (Pydantic)
  * `500` erro interno (ex.: renderização PDF)

## 5) Reuso da UI (Streamlit) no design da API

A API replica decisões da UI:

* **Seleção de período**: informar `mes` **ou** `mes_nome`. Se ambos ausentes, assume **mês anterior** ao mês corrente.
* **Multi-cliente**: aceite de múltiplos `cliente_ids` e nome exibido automático `"<NomeBase>_Consolidado"`.
* **Índice**: sempre insere o “Índice” como primeira seção do PDF.
* **Relatório 8 (Parecer)**: aceita HTML (Quill), que é **normalizado** via `processar_html_parecer`.

## 6) Estrutura do código (API)

Arquivo principal: `src/api/main.py`

* **Segurança**: API key (header `X-API-Key`)
* **Utilitários**:

  * `get_mes_numero(mes, mes_nome)`: prioriza número; aceita nome (via `obter_meses()`); default mês anterior.
  * `default_ano(ano)`: se vazio, ano atual.
  * `verificar_permissoes(is_admin, is_consultant)`: exige ao menos um True.
  * `processar_html_parecer(html)`: converte classes Quill para CSS inline.
  * `slugify_filename(text)`: para nomes de arquivo.
* **Endpoints**:

  * `GET /v1/health`
  * `GET /v1/clientes`
  * `GET /v1/anos?cliente_ids=...`
  * `GET /v1/meta` *(hoje público; recomendado proteger em prod)*
  * `POST /v1/relatorios/pdf` *(principal)*
  * `GET /v1/relatorios/pdf` *(compat teste via query params)*

## 7) Estendendo a API

### 7.1 Adicionar um novo tipo de relatório (ex.: “Relatório 9”)

1. Criar classe `Relatorio9` em `src/core/relatorios`.
2. Importar no `main.py`.
3. Incluir no mapeamento `relatorios_classes`.
4. (Opcional) Ajustar UI/`/v1/meta` para exibir o novo ID.
5. Garantir que `gerar_relatorio(...)` aceite as mesmas assinaturas de data usadas hoje.

### 7.2 Novos endpoints

* Siga o padrão:

  * `response_model` claro (quando aplicável).
  * Tipagem estrita nos parâmetros (Pydantic/Query).
  * `summary`/`description` para Swagger.
  * Tratamento de erro com mensagens objetivas.

## 8) Testes

* Use `fastapi.testclient.TestClient` para testes de integração.
* “Happy path” essencial:

  * `GET /v1/health`
  * `GET /v1/clientes`
  * `GET /v1/anos?cliente_ids=...`
  * `POST /v1/relatorios/pdf` com 1 e com N clientes
  * `Relatório 8` com `analise_text` (HTML)
* “Sad path”:

  * 401 sem `X-API-Key` (quando `API_KEY` estiver setado)
  * 403 sem permissões
  * 422 com payload inválido (mês fora do range, listas vazias, etc.)

## 9) Observabilidade & Operação

* **/v1/health** para liveness.
* Logs: delegados ao servidor/app (configure Uvicorn/Gunicorn + logging do projeto).
* Storage:

  * PDFs são gerados em `outputs/` antes do streaming. Garanta **permissão de escrita** e **limpeza** periódica no ambiente.

## 10) Checklist de Onboarding

* [ ] Instale wkhtmltopdf
* [ ] Configure variáveis de DB e `API_KEY`
* [ ] Rode `uvicorn src.api.main:app --reload`
* [ ] Teste `/docs` e gere um PDF simples
* [ ] Revise CORS/domínios em prod
* [ ] Habilite logs e rotação de arquivos de saída (se aplicável)

---

# Endpoints & Payloads — Referência Rápida

## Autenticação

* **Header**: `X-API-Key: <sua-chave>`
* Sem `API_KEY` no servidor → **sem exigência** de header (modo dev).

## Tabela de endpoints

|   Método | Rota                     | Auth | Descrição                                          |
| -------: | ------------------------ | :--: | -------------------------------------------------- |
|      GET | `/v1/health`             |   ✅  | Health check                                       |
|      GET | `/v1/clientes`           |   ✅  | Lista clientes ativos (`id_cliente`, `nome`)       |
|      GET | `/v1/anos`               |   ✅  | Anos disponíveis para os clientes informados       |
|      GET | `/v1/meta`               | 🚫\* | Metadados: meses (nome/número) e IDs de relatórios |
| **POST** | **`/v1/relatorios/pdf`** |   ✅  | **Gera PDF dos relatórios selecionados**           |
|      GET | `/v1/relatorios/pdf`     |   ✅  | Igual ao POST, mas via query params (para testes)  |

\* Observação: `/v1/meta` não exige API Key no código atual. Recomenda-se proteger em produção.

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
  "is_admin": true,
  "is_consultant": false,
  "user_id": "123",
  "user_name": "Danielle",
  "multi_cliente": true,
  "cliente_ids": [10, 20],
  "display_cliente_nome": null,
  "mes": 7,
  "mes_nome": null,
  "ano": 2025,
  "relatorios": ["Relatório 1", "Relatório 6", "Relatório 7", "Relatório 8"],
  "analise_text": "<p><span class=\"ql-size-large\"><strong>Visão Geral:</strong></span> Margem saudável.</p>",
  "marca": "Sim"
}
```

#### Regras importantes

* **Permissões**: `is_admin` **ou** `is_consultant` precisa ser `true` → senão `403`.
* **Período**:

  * informe **`mes`** (1–12) **ou** **`mes_nome`** (ex.: `"Julho"`).
  * se ambos ausentes → mês **anterior** ao atual.
  * `ano` ausente → ano atual.
* **Multi-cliente**:

  * se `multi_cliente=true` e `cliente_ids` > 1 e `display_cliente_nome` vazio → API gera `"<NomeBase>_Consolidado"`.
* **Relatórios**: lista com qualquer subset de `"Relatório 1"` … `"Relatório 8"`.

  * `"Relatório 8"` (parecer) aceita `analise_text` (HTML) e normaliza CSS automaticamente.
* **Saída**: PDF é salvo em `outputs/` e enviado no corpo da resposta (streaming).
* **Observação**: `user_id` e `user_name` são opcionais e hoje não usados, mas podem ser úteis para logs/auditoria.

#### Respostas

* **200**: `application/pdf` (stream)
* **401**: API Key ausente/errada (se `API_KEY` setado)
* **403**: sem permissão (nenhum de `is_admin`/`is_consultant`)
* **422**: payload inválido (ex.: `mes` fora de 1–12, `relatorios` vazio)
* **500**: erro interno (ex.: falha no wkhtmltopdf)

### Exemplos de chamada

**cURL**

```bash
curl -X POST "http://localhost:8000/v1/relatorios/pdf" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  --data '{
    "is_admin": true,
    "is_consultant": false,
    "multi_cliente": false,
    "cliente_ids": [10],
    "mes_nome": "Junho",
    "ano": 2025,
    "relatorios": ["Relatório 1","Relatório 2","Relatório 6"],
    "marca": "Sim"
  }' \
  --output Relatorio_ACME_Junho_2025.pdf
```

**Python (requests)**

```python
import requests

url = "http://localhost:8000/v1/relatorios/pdf"
headers = {"X-API-Key": "minha-chave", "Content-Type": "application/json"}
payload = {
    "is_admin": True,
    "is_consultant": False,
    "multi_cliente": True,
    "cliente_ids": [10, 20],
    "mes": 7,
    "ano": 2025,
    "relatorios": ["Relatório 7", "Relatório 8"],
    "analise_text": "<p><span class=\"ql-size-large\">OK</span></p>",
    "marca": "Não"
}

r = requests.post(url, headers=headers, json=payload)
open("Relatorio_Consolidado.pdf", "wb").write(r.content)
```

**JavaScript (fetch)**

```js
const res = await fetch("http://localhost:8000/v1/relatorios/pdf", {
  method: "POST",
  headers: {
    "X-API-Key": "minha-chave",
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    is_admin: true,
    is_consultant: false,
    multi_cliente: false,
    cliente_ids: [10],
    relatorios: ["Relatório 6","Relatório 7"]
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

## `/v1/relatorios/pdf` — GET (modo “rápido”, via query)

Mesmos comportamentos do POST, mas usando query params. Útil para testar no navegador.

**Exemplo**

``` 
GET /v1/relatorios/pdf
  ?is_admin=true
  &is_consultant=false
  &multi_cliente=false
  &cliente_ids=10
  &mes_nome=Maio
  &ano=2025
  &relatorios=Relatório%206,Relatório%207
```

> Dica: `analise_text` também pode ser enviado por query, mas para HTML é mais seguro usar `POST`.

---

## Mapeamento de relatórios

| ID            | Classe          | Observações de chamada                     |
| ------------- | --------------- | ------------------------------------------ |
| Relatório 1–4 | `Relatorio1..4` | `gerar_relatorio(mes_atual, mes_anterior)` |
| Relatório 5   | `Relatorio5`    | `gerar_relatorio(mes_atual)`               |
| Relatório 6   | `Relatorio6`    | `gerar_relatorio(mes_atual)`               |
| Relatório 7   | `Relatorio7`    | `gerar_relatorio(mes_atual)`               |
| Relatório 8   | `Relatorio8`    | aceita `salvar_analise(mes_atual, html)`   |

---

## Mensagens de erro (amostras)

```json
// 401
{ "detail": "Invalid or missing API Key" }

// 403
{ "detail": "Acesso negado: apenas administradores ou consultores." }

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
{ "detail": "Erro ao gerar PDF: <mensagem>" }
```

---

## Boas práticas para produção

* **Proteja `/v1/meta`** com a mesma API Key (ou roles).
* **Restringa CORS** a domínios confiáveis.
* **Rotacione/limpe `outputs/`** (os PDFs são gravados antes do streaming).
* **Observabilidade**: centralize logs do Uvicorn + métricas do host.
* **Segurança das permissões**: migre de flags booleanas de payload para **RBAC/JWT**.
