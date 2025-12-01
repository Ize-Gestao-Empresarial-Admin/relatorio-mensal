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
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    # Debug log
    logging.info(f"API_KEY from env (first 10 chars): {API_KEY[:10] if API_KEY else 'None'}")
    logging.info(f"Received x_api_key (first 10 chars): {x_api_key[:10] if x_api_key else 'None'}")
    logging.info(f"API_KEY length: {len(API_KEY) if API_KEY else 0}")
    logging.info(f"x_api_key length: {len(x_api_key) if x_api_key else 0}")
    
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
    
    # NOVO: Filtro por centro de custo/empresa
    centro_custo: bool = Field(default=False, description="Se True, gera um relatório por centro de custo/empresa")

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
# Funções auxiliares de geração de relatórios
# ---------------------------
def gerar_relatorio_unico(
    db: DatabaseConnection,
    id_cliente: List[int],
    display_nome: str,
    mes_atual: date,
    mes_anterior: date,
    relatorios_ids: List[int],
    analise_text: str,
    centro_custo: Optional[str],
    empresa: Optional[str],
    ano: int,
    mes: int
) -> StreamingResponse:
    """Gera um único relatório PDF (com ou sem filtro de centro de custo/empresa)."""
    
    # Criar instância de Indicadores
    indicadores = Indicadores(id_cliente, db)
    
    # Validação de dados
    dados_validos, mensagem_erro = validar_dados_cliente(indicadores, mes_atual)
    if not dados_validos:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "Dados insuficientes",
                "message": mensagem_erro,
                "cliente_id": id_cliente,
                "periodo": f"{mes}/{ano}",
                "code": "NO_DATA_AVAILABLE"
            }
        )
    
    # Índice
    meses = obter_meses()
    nome_mes = next((nm for nm, n in meses if n == mes), str(mes))
    ids_escolhidos = set(relatorios_ids)
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
    
    # Gerar relatórios
    for rel_id in relatorios_ids:
        rel_label = RELATORIO_LABELS[rel_id]
        rel_class = RELATORIO_CLASSES[rel_id]
        relatorio = rel_class(indicadores, display_nome)
        
        # Passar filtros para os métodos das classes de relatório
        if rel_id in {1, 2, 3, 4, 5}:  # Relatórios de FC (aceita centro_custo)
            dados = relatorio.gerar_relatorio(mes_atual, mes_anterior, centro_custo)
        elif rel_id == 6:  # Relatório DRE (aceita empresa)
            dados = relatorio.gerar_relatorio(mes_atual, empresa)
        elif rel_id == 7:  # Relatório de indicadores (sem filtro)
            dados = relatorio.gerar_relatorio(mes_atual)
        elif rel_id == 8:  # Notas do consultor (sem filtro)
            if analise_text:
                relatorio.salvar_analise(mes_atual, analise_text)
            dados = relatorio.gerar_relatorio(mes_atual)
        
        relatorios_dados.append((rel_label, dados))
    
    # Renderizar PDF
    engine = RenderingEngine()
    os.makedirs("outputs", exist_ok=True)
    
    # Nome do arquivo
    nome_mes_slug = slugify_filename(nome_mes)
    filename_parts = [f"Relatorio_{slugify_filename(display_nome)}", f"{nome_mes_slug}_{ano}"]
    
    if centro_custo:
        filename_parts.append(f"CC_{slugify_filename(centro_custo)}")
    elif empresa:
        filename_parts.append(f"EMP_{slugify_filename(empresa)}")
        
    filename = "_".join(filename_parts) + ".pdf"
    output_path = os.path.join("outputs", filename)
    pdf_path = engine.render_to_pdf(relatorios_dados, display_nome, nome_mes, ano, output_path)
    
    # Retornar arquivo
    pdf_bytes = open(pdf_path, "rb").read()
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename=\"{filename}\"'}
    )


def gerar_multiplos_pdfs(
    db: DatabaseConnection,
    id_cliente: List[int],
    display_nome: str,
    mes_atual: date,
    mes_anterior: date,
    relatorios_ids: List[int],
    analise_text: str,
    centros_custo: List[str],
    ano: int,
    mes: int
) -> StreamingResponse:
    """Gera múltiplos PDFs (um por centro de custo/empresa) e retorna como ZIP."""
    
    meses = obter_meses()
    nome_mes = next((nm for nm, n in meses if n == mes), str(mes))
    nome_mes_slug = slugify_filename(nome_mes)
    
    def gerar_pdf_para_centro(centro: str) -> tuple[str, bytes]:
        """
        Função auxiliar para gerar PDF de um centro de custo específico.
        Retorna tupla (filename, pdf_bytes) para ser adicionada ao ZIP.
        """
        # Criar instância de Indicadores para este centro de custo
        indicadores = Indicadores(id_cliente, db)
        
        # Índice
        ids_escolhidos = set(relatorios_ids)
        indice_data = {
            "fluxo_caixa": "Sim" if ids_escolhidos & {1, 2, 3, 4, 5} else "Não",
            "dre_gerencial": "Sim" if 6 in ids_escolhidos else "Não",
            "indicador": "Sim" if 7 in ids_escolhidos else "Não",
            "nota_consultor": "Sim" if 8 in ids_escolhidos else "Não",
            "cliente_nome": f"{display_nome} - {centro}",
            "mes": nome_mes,
            "ano": ano,
            "nome": f"{display_nome} - {centro}",
            "Periodo": f"{nome_mes} {ano}",
            "marca": MARCA_PADRAO,
        }
        
        relatorios_dados = [("Índice", indice_data)]
        
        # Gerar relatórios para este centro
        for rel_id in relatorios_ids:
            rel_label = RELATORIO_LABELS[rel_id]
            rel_class = RELATORIO_CLASSES[rel_id]
            relatorio = rel_class(indicadores, f"{display_nome} - {centro}")
            
            # Passar centro_custo/empresa para os métodos das classes de relatório
            if rel_id in {1, 2, 3, 4, 5}:  # Relatórios de FC (aceita centro_custo)
                dados = relatorio.gerar_relatorio(mes_atual, mes_anterior, centro)
            elif rel_id == 6:  # Relatório DRE (aceita empresa)
                dados = relatorio.gerar_relatorio(mes_atual, centro)
            elif rel_id == 7:  # Relatório de indicadores (sem filtro)
                dados = relatorio.gerar_relatorio(mes_atual)
            elif rel_id == 8:  # Notas do consultor (sem filtro)
                if analise_text:
                    relatorio.salvar_analise(mes_atual, analise_text)
                dados = relatorio.gerar_relatorio(mes_atual)
            
            relatorios_dados.append((rel_label, dados))
        
        # Nome do arquivo individual
        filename = f"Relatorio_{slugify_filename(display_nome)}_{nome_mes_slug}_{ano}_CC_{slugify_filename(centro)}.pdf"
        output_path = os.path.join("outputs", filename)
        
        # Renderizar PDF
        engine = RenderingEngine()
        pdf_path = engine.render_to_pdf(relatorios_dados, f"{display_nome} - {centro}", nome_mes, ano, output_path)
        
        # Ler o PDF em bytes
        with open(pdf_path, 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()
        
        # Limpar arquivo temporário
        try:
            os.remove(pdf_path)
        except:
            pass
        
        return (filename, pdf_bytes)
    
    # Processar centros de custo em paralelo
    pdfs_gerados = {}
    max_workers = min(len(centros_custo), os.cpu_count() or 4)  # Limita ao número de CPUs disponíveis
    
    logging.info(f"Gerando {len(centros_custo)} PDFs em paralelo com {max_workers} workers...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submeter todas as tarefas
        future_to_centro = {executor.submit(gerar_pdf_para_centro, centro): centro for centro in centros_custo}
        
        # Coletar resultados conforme vão sendo completados
        for future in as_completed(future_to_centro):
            centro = future_to_centro[future]
            try:
                filename, pdf_bytes = future.result()
                pdfs_gerados[filename] = pdf_bytes
                logging.info(f"PDF gerado com sucesso para centro: {centro}")
            except Exception as e:
                logging.error(f"Erro ao gerar PDF para centro {centro}: {str(e)}")
                # Continua processando os outros mesmo se um falhar
    
    # Criar arquivo ZIP em memória com os PDFs gerados
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, pdf_bytes in pdfs_gerados.items():
            zip_file.writestr(filename, pdf_bytes)
    
    # Retornar ZIP
    zip_buffer.seek(0)
    zip_filename = f"Relatorios_{slugify_filename(display_nome)}_{nome_mes_slug}_{ano}_CentrosCusto.zip"
    
    logging.info(f"ZIP criado com {len(pdfs_gerados)} PDFs: {zip_filename}")
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename=\"{zip_filename}\"'}
    )

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

    # 4) Preparar geração
    db = DatabaseConnection()
    
    # 4.1) NOVO: Verificar se deve filtrar por centro de custo
    if payload.centro_custo:
        # Buscar centros de custo disponíveis
        centros_custo = buscar_centros_custo_disponiveis(db, id_cliente, ano, mes)
        
        if not centros_custo:
            raise HTTPException(
                status_code=404, 
                detail={
                    "error": "Nenhum centro de custo encontrado",
                    "message": "Não foram encontrados centros de custo ou empresas com dados para o período especificado.",
                    "cliente_id": id_cliente,
                    "periodo": f"{mes}/{ano}",
                    "code": "NO_COST_CENTER_FOUND"
                }
            )
        
        # Gerar múltiplos PDFs (um por centro de custo)
        return gerar_multiplos_pdfs(
            db, id_cliente, display_nome, mes_atual, mes_anterior,
            payload.relatorios, analise_text, centros_custo, ano, mes
        )
    
    # 4.2) Geração padrão (sem filtro, todos os centros somados)
    indicadores = Indicadores(id_cliente, db)

    # Validar se o cliente possui dados válidos para o período
    dados_validos, mensagem_erro = validar_dados_cliente(indicadores, mes_atual)
    if not dados_validos:
        raise HTTPException(
            status_code=422, 
            detail={
                "error": "Dados insuficientes",
                "message": mensagem_erro,
                "cliente_id": id_cliente,
                "periodo": f"{mes}/{ano}",
                "code": "NO_DATA_AVAILABLE"
            }
        )

    # Gerar relatório único
    return gerar_relatorio_unico(
        db, id_cliente, display_nome, mes_atual, mes_anterior,
        payload.relatorios, analise_text, None, None, ano, mes
    )

# ---------------------------
# Helpers de validação de dados
# ---------------------------
def buscar_centros_custo_disponiveis(db: DatabaseConnection, id_cliente: List[int], ano: int, mes: int) -> List[str]:
    """
    Retorna lista de centros de custo/empresas com dados no período.
    Busca na tabela FC (coluna centro_custo) e DRE (coluna empresa).
    
    Args:
        db: Conexão com banco de dados
        id_cliente: Lista de IDs de clientes
        ano: Ano do período
        mes: Mês do período
        
    Returns:
        Lista de strings com os centros de custo/empresas disponíveis
    """
    from sqlalchemy import text
    
    # Buscar centros de custo da tabela FC
    query_fc = text("""
        SELECT DISTINCT centro_custo
        FROM fc 
        WHERE id_cliente = ANY (:id_cliente)
          AND EXTRACT(YEAR FROM data) = :year
          AND EXTRACT(MONTH FROM data) = :month
          AND centro_custo IS NOT NULL
          AND TRIM(centro_custo) != ''
        ORDER BY centro_custo;
    """)
    
    # Buscar empresas da tabela DRE
    query_dre = text("""
        SELECT DISTINCT empresa
        FROM dre 
        WHERE id_cliente = ANY (:id_cliente)
          AND EXTRACT(YEAR FROM data) = :year
          AND EXTRACT(MONTH FROM data) = :month
          AND empresa IS NOT NULL
          AND TRIM(empresa) != ''
        ORDER BY empresa;
    """)
    
    params = {
        "id_cliente": id_cliente,
        "year": ano,
        "month": mes
    }
    
    try:
        result_fc = db.execute_query(query_fc, params)
        result_dre = db.execute_query(query_dre, params)
        
        centros_fc = [row["centro_custo"] for _, row in result_fc.iterrows()] if not result_fc.empty else []
        empresas_dre = [row["empresa"] for _, row in result_dre.iterrows()] if not result_dre.empty else []
        
        # Unir as duas listas e remover duplicatas mantendo a ordem
        todos = centros_fc + [e for e in empresas_dre if e not in centros_fc]
        
        return todos if todos else []
        
    except Exception as e:
        logging.error(f"Erro ao buscar centros de custo: {str(e)}")
        return []

def validar_dados_cliente(indicadores: Indicadores, mes_atual: date) -> tuple[bool, str]:
    """
    Valida se o cliente possui dados válidos (não zerados/nulos) para o período especificado.
    
    Args:
        indicadores: Instância de Indicadores do cliente
        mes_atual: Data do mês para validação
        
    Returns:
        Tupla (dados_validos: bool, mensagem_erro: str)
    """
    try:
        # Verificar receitas
        receitas = indicadores.calcular_receitas_fc(mes_atual, '3.%')
        receita_total = sum(float(r.get('total_categoria', 0)) for r in receitas) if receitas else 0
        
        # Verificar custos variáveis
        custos = indicadores.calcular_custos_variaveis_fc(mes_atual, '4.%')
        custos_total = sum(abs(float(c.get('total_categoria', 0))) for c in custos) if custos else 0
        
        # Verificar despesas fixas
        despesas = indicadores.calcular_despesas_fixas_fc(mes_atual)
        despesas_total = sum(abs(float(d.get('total_categoria', 0))) for d in despesas) if despesas else 0
        
        # Validar se há pelo menos alguma movimentação financeira significativa
        # Considera dados válidos se há receita OU movimentação de custos/despesas
        has_receita = receita_total > 0
        has_movimentacao = custos_total > 0 or despesas_total > 0
        
        if not has_receita and not has_movimentacao:
            # Se não há nenhuma movimentação, verificar se há pelo menos registros na base
            if not receitas and not custos and not despesas:
                return False, "Não foram encontrados dados financeiros para este cliente no período especificado."
            else:
                return False, "Os dados financeiros do cliente estão zerados para o período especificado."
        
        # Se há receita mas não há custos/despesas, pode ser válido (empresa sem custos no período)
        # Se há custos/despesas mas não receita, pode indicar problema nos dados
        if has_receita or has_movimentacao:
            return True, ""
            
        return False, "Dados financeiros inconsistentes encontrados para o período."
        
    except Exception as e:
        return False, f"Erro ao validar dados do cliente: {str(e)}"

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
