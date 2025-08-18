from fastapi import FastAPI, HTTPException, Query, Depends, Security
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date, timedelta
import os
import io
import re
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis do arquivo .env

import logging
from src.database.db_utils import DatabaseConnection, buscar_clientes, obter_meses, obter_anos
from src.core.indicadores import Indicadores
from src.core.relatorios import (
    Relatorio1, Relatorio2, Relatorio3, Relatorio4, Relatorio5, Relatorio6, Relatorio7, Relatorio8
)
from src.rendering.engine import RenderingEngine

# --- Mapas: ID numérico -> Classe e Nome de exibição ---
RELATORIO_CLASSES = {
    1: Relatorio1, 2: Relatorio2, 3: Relatorio3, 4: Relatorio4,
    5: Relatorio5, 6: Relatorio6, 7: Relatorio7, 8: Relatorio8
}

RELATORIO_LABELS = {
    1: "Relatório 1", 2: "Relatório 2", 3: "Relatório 3", 4: "Relatório 4",
    5: "Relatório 5", 6: "Relatório 6", 7: "Relatório 7", 8: "Relatório 8"
}

# ---------------------------
# Configuração FastAPI
# ---------------------------
app = FastAPI(
    title="IZE Relatórios Mensais - API",
    version="1.0.0",
    description="API para geração de relatórios financeiros PDF usando as mesmas regras do app Streamlit.",
    swagger_ui_parameters={"persistAuthorization": True}  # mantém autorização no Swagger
)

# ---------------------------
# Segurança: API Key simples via header
# ---------------------------
API_KEY = os.getenv("API_KEY")  # Sem default: força configurar em produção
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(x_api_key: Optional[str] = Security(api_key_header)):
    """
    Exige a presença de X-API-Key no header com o mesmo valor de API_KEY (.env).
    - 401 se a chave não vier ou for inválida
    - 500 se API_KEY não estiver configurada
    """
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Configuração inválida: defina API_KEY no ambiente (.env).")
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Não autenticado: forneça X-API-Key válida.")
    return True

# CORS (ajuste domínios conforme sua necessidade)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, restrinja
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Constantes de Negócio
# ---------------------------
MARCA_PADRAO = "Sim"  # marca fixa e interna

# ---------------------------
# Helpers (mesmos do Streamlit)
# ---------------------------
def processar_html_parecer(html_content: str) -> str:
    """Processa o HTML do editor Quill para PDF (mesma lógica do app)."""
    if not html_content:
        return ""
    size_mapping = {
        'ql-size-small': 'font-size: 12px;',
        'ql-size-normal': 'font-size: 14px;',
        'ql-size-large': 'font-size: 20px;',
        'ql-size-huge': 'font-size: 24px;'
    }
    processed_html = html_content
    for quill_class, css_style in size_mapping.items():
        # Substitui <span class="ql-size-X">...</span> por <span style="font-size: Ypx;">...</span>
        pattern = rf'<span class="{quill_class}">(.*?)</span>'
        replacement = rf'<span style="{css_style}">\1</span>'
        processed_html = re.sub(pattern, replacement, processed_html, flags=re.DOTALL)
    return processed_html

def slugify_filename(text: str) -> str:
    # Sanitiza o nome do arquivo: espaços e caracteres especiais -> underscore
    text = re.sub(r"\s+", "_", text.strip())
    text = re.sub(r"[^\w\-\.]", "_", text, flags=re.UNICODE)
    return text

def get_mes_numero(mes: Optional[int]) -> int:
    """Aceita mês por número (1-12)."""
    if mes is not None:
        if 1 <= mes <= 12:
            return mes
        raise HTTPException(status_code=422, detail="Parâmetro 'mes' deve estar entre 1 e 12.")
    # default: mês anterior ao atual
    hoje = date.today().replace(day=1)
    mes_anterior = (hoje - timedelta(days=1)).month
    return mes_anterior

def default_ano(ano: Optional[int]) -> int:
    return ano if ano else date.today().year

# ---------------------------
# Modelos Pydantic
# ---------------------------
class RelatorioRequest(BaseModel):
    # Seleção de clientes (sem multi_cliente; aceita consolidado via lista > 1)
    id_cliente: List[int] = Field(..., min_length=1, description="IDs de cliente(s)")

    # Período
    mes: Optional[int] = Field(default=None, ge=1, le=12)
    ano: Optional[int] = None

    # Relatórios e opções: exige IDs 1..8 (pode entrar como string 'Relatório 7' que normalizamos)
    relatorios: List[int] = Field(..., min_length=1, description="IDs dos relatórios (1 a 8)")
    analise_text: Optional[str] = None

    @field_validator("relatorios", mode="before")
    @classmethod
    def normalizar_relatorios_para_ids(cls, v):
        """
        Aceita:
          - [1, 7, 8]
          - ["1","7","8"]
          - ["Relatório 7","Relatorio 8","3"]
          - "7,8" ou "Relatório 7, Relatório 8"
        Converte para lista de ints únicos 1..8, preservando a ordem.
        """
        def extrair_id(item):
            if isinstance(item, int):
                return item
            if isinstance(item, str):
                m = re.search(r"\d+", item)
                if m:
                    return int(m.group())
            raise ValueError(f"Valor inválido em 'relatorios': {item}")

        # Normaliza para lista de tokens
        if isinstance(v, str):
            tokens = re.split(r"[,\s]+", v.strip())
            tokens = [t for t in tokens if t]  # remove vazios
        elif isinstance(v, list):
            tokens = v
        else:
            raise ValueError("Formato inválido para 'relatorios'.")

        # Converte para int e valida faixa
        ids = [extrair_id(t) for t in tokens]
        for n in ids:
            if not (1 <= n <= 8):
                raise ValueError("IDs de relatório devem estar entre 1 e 8.")

        # Deduplica preservando ordem
        vistos, unicos = set(), []
        for n in ids:
            if n not in vistos:
                vistos.add(n)
                unicos.append(n)
        return unicos

    @field_validator("relatorios")
    @classmethod
    def validar_relatorios_nao_vazios(cls, v):
        if not v:
            raise ValueError("Selecione pelo menos um relatório.")
        return v

# ---------------------------
# Endpoints utilitários (todos protegidos por API Key)
# ---------------------------
@app.get("/v1/health", dependencies=[Depends(verify_api_key)])
def health():
    return {"status": "ok"}

@app.get("/v1/clientes", dependencies=[Depends(verify_api_key)])
def listar_clientes():
    db = DatabaseConnection()
    clientes = buscar_clientes(db)  # lista de dicts {id_cliente, nome}
    return {"clientes": clientes or []}

@app.get("/v1/anos", dependencies=[Depends(verify_api_key)])
def listar_anos(id_cliente: str = Query(..., description="IDs separados por vírgula, ex: 10,20")):
    db = DatabaseConnection()
    # Converte CSV de IDs em lista de ints
    ids = [int(x) for x in id_cliente.split(",") if x.strip().isdigit()]
    if not ids:
        raise HTTPException(status_code=422, detail="Informe id_cliente válidos.")
    todos = []
    for cid in ids:
        anos_c = obter_anos(db, cid)  # ex.: [2025, 2024, ...]
        todos.extend(anos_c or [])
    # únicos e ordenados desc
    anos = sorted(list(set(todos)), reverse=True)
    return {"anos": anos}

@app.get("/v1/meta", dependencies=[Depends(verify_api_key)])
def meta():
    meses = obter_meses()  # [(nome, numero)]
    relatorios = [RELATORIO_LABELS[i] for i in range(1, 9)]
    return {"meses": meses, "relatorios": relatorios}

# ---------------------------
# Endpoint principal: gera PDF (POST recomendado)
# ---------------------------
@app.post("/v1/relatorios/pdf", dependencies=[Depends(verify_api_key)])
def gerar_pdf(payload: RelatorioRequest):
    # 1) Período
    mes = get_mes_numero(payload.mes)
    ano = default_ano(payload.ano)
    mes_atual = date(ano, mes, 1)
    mes_anterior = (mes_atual - timedelta(days=1)).replace(day=1)

    # 2) Clientes
    id_cliente = payload.id_cliente  # SEMPRE lista (suporta consolidado)
    is_consolidado = len(id_cliente) > 1

    # Nome exibido sempre derivado do banco (ou fallback para Cliente_<id>)
    db_tmp = DatabaseConnection()
    all_cli = buscar_clientes(db_tmp) or []
    mapa = {c["id_cliente"]: c["nome"] for c in all_cli}
    base = mapa.get(id_cliente[0], f"Cliente_{id_cliente[0]}")
    display_nome = f"{base}_Consolidado" if is_consolidado else base

    # 3) Análise do consultor (se houver)
    analise_text = processar_html_parecer(payload.analise_text or "")

    # 4) Preparar geração (mesma lógica da UI)
    db = DatabaseConnection()
    indicadores = Indicadores(id_cliente, db)  # passa a lista (suporta consolidado)

    # Índice (igual à UI)
    meses = obter_meses()
    nome_mes = next((nm for nm, n in meses if n == mes), str(mes))
    ids_escolhidos = set(payload.relatorios)
    indice_data = {
        "fluxo_caixa": "Sim" if ids_escolhidos & {1, 2, 3, 4, 5} else "Não",
        "dre_gerencial": "Sim" if 6 in ids_escolhidos else "Não",
        "indicador": "Sim" if 7 in ids_escolhidos else "Não",
        "nota_consultor": "Sim" if 8 in ids_escolhidos else "Não",
        "cliente_nome": display_nome,
        "mes": nome_mes,
        "ano": ano,
        "nome": display_nome,
        "Periodo": f"{nome_mes} {ano}",
        "marca": MARCA_PADRAO,
    }

    relatorios_dados = [("Índice", indice_data)]

    for rel_id in payload.relatorios:
        rel_label = RELATORIO_LABELS[rel_id]
        rel_class = RELATORIO_CLASSES[rel_id]
        relatorio = rel_class(indicadores, display_nome)

        if rel_id in {1, 2, 3, 4}:
            dados = relatorio.gerar_relatorio(mes_atual, mes_anterior)
        elif rel_id == 8:
            if analise_text:
                relatorio.salvar_analise(mes_atual, analise_text)
            dados = relatorio.gerar_relatorio(mes_atual)
        else:
            dados = relatorio.gerar_relatorio(mes_atual)

        relatorios_dados.append((rel_label, dados))

    # 5) Renderizar PDF (mesmo engine)
    engine = RenderingEngine()
    os.makedirs("outputs", exist_ok=True)
    filename = f"Relatorio_{slugify_filename(display_nome)}_{slugify_filename(nome_mes)}_{ano}.pdf"
    output_path = os.path.join("outputs", filename)
    pdf_path = engine.render_to_pdf(relatorios_dados, display_nome, nome_mes, ano, output_path)

    # 6) Responder como arquivo
    pdf_bytes = open(pdf_path, "rb").read()
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename=\"{filename}\"'}
    )

# ---------------------------
# Endpoint GET compatível com query params "estilo Streamlit"
# (útil para testes rápidos via navegador)
# ---------------------------
@app.get("/v1/relatorios/pdf", dependencies=[Depends(verify_api_key)])
def gerar_pdf_get(
    id_cliente: str = Query(..., description="IDs separados por vírgula"),
    mes: Optional[int] = Query(None, ge=1, le=12),
    ano: Optional[int] = None,
    relatorios: str = Query(..., description="Lista separada por vírgula. Ex: 7,8 ou 'Relatório 7, Relatório 8'"),
    analise_text: Optional[str] = None,
):
    # Converte os query params em payload Pydantic (validator normaliza relatorios para ints)
    payload = RelatorioRequest(
        id_cliente=[int(x) for x in id_cliente.split(",") if x.strip().isdigit()],
        mes=mes,
        ano=ano,
        relatorios=[x.strip() for x in relatorios.split(",") if x.strip()],
        analise_text=analise_text
    )
    return gerar_pdf(payload)
