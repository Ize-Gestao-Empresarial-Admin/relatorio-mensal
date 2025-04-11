from fastapi import FastAPI, HTTPException, Query, Body, Response, Depends
from fastapi.responses import FileResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import date, datetime
import os
from sqlalchemy.orm import Session
import tempfile

from src.core.indicadores import Indicadores
from src.core.relatorios.relatorio_1 import Relatorio1
from src.core.relatorios.relatorio_2 import Relatorio2
from src.core.relatorios.relatorio_3 import Relatorio3
from src.core.relatorios.relatorio_4 import Relatorio4
from src.core.relatorios.relatorio_5 import Relatorio5
from src.core.relatorios.relatorio_6 import Relatorio6
from src.core.relatorios.relatorio_7 import Relatorio7
from src.database.db_utils import DatabaseConnection, buscar_clientes, obter_meses
from src.interfaces.pdf_generator import PDFGenerator

app = FastAPI(
    title="API de Relatórios Financeiros",
    description="""
    API para geração de relatórios financeiros para clientes.
    Suporta 7 tipos de relatórios que podem ser obtidos individualmente ou combinados em um PDF.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Modelos de dados para validação e documentação
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

# Helper para obter conexão com banco
def get_db():
    db = DatabaseConnection()
    return db

@app.get("/clientes", 
         response_model=List[Dict[str, Any]],
         summary="Lista todos os clientes ativos",
         description="Retorna uma lista de todos os clientes ativos no sistema.")
def listar_clientes(db: DatabaseConnection = Depends(get_db)):
    """Busca todos os clientes ativos no sistema."""
    return buscar_clientes(db)

@app.get("/meses", 
         response_model=List[Dict[str, Any]],
         summary="Lista todos os meses disponíveis",
         description="Retorna uma lista com os nomes e números dos meses.")
def listar_meses():
    """Retorna lista de meses para seleção."""
    return [{"nome": nome, "numero": num} for nome, num in obter_meses()]

@app.get("/relatorio/{tipo}/{id_cliente}/{mes}/{ano}", 
         response_model=Dict[str, Any],
         summary="Obtém um relatório específico",
         description="Gera um relatório financeiro específico para um cliente, mês e ano.")
def get_relatorio(
    tipo: int, 
    id_cliente: int, 
    mes: int, 
    ano: int, 
    mes_anterior: bool = Query(True, description="Incluir comparação com mês anterior"),
    db: DatabaseConnection = Depends(get_db)
):
    """
    Gera um relatório financeiro específico para um cliente, mês e ano.
    
    - **tipo**: Tipo de relatório (1-7)
    - **id_cliente**: ID do cliente
    - **mes**: Número do mês (1-12)
    - **ano**: Ano do relatório
    - **mes_anterior**: Se deve incluir comparação com o mês anterior
    """
    # Validação básica
    if tipo < 1 or tipo > 7:
        raise HTTPException(status_code=400, detail="Tipo de relatório inválido (deve ser 1-7)")
    if mes < 1 or mes > 12:
        raise HTTPException(status_code=400, detail="Mês inválido (deve ser 1-12)")
    
    # Busca cliente
    clientes = buscar_clientes(db)
    cliente = next((c for c in clientes if c["id_cliente"] == id_cliente), None)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    nome_cliente = cliente["nome"]
    
    # Instancia indicadores
    indicadores = Indicadores(id_cliente, db)
    
    # Cria as datas
    mes_atual = date(ano, mes, 1)
    mes_anterior_data = date(ano, mes - 1, 1) if mes > 1 else date(ano - 1, 12, 1) if mes_anterior else None
    
    # Seleciona a classe de relatório adequada
    relatorio_classes = {
        1: Relatorio1,
        2: Relatorio2,
        3: Relatorio3,
        4: Relatorio4,
        5: Relatorio5,
        6: Relatorio6,
        7: Relatorio7
    }
    
    relatorio_class = relatorio_classes[tipo]
    rel_instance = relatorio_class(indicadores, nome_cliente)
    
    # Gera o relatório
    if tipo in [1, 2, 3] and mes_anterior:
        relatorio_data = rel_instance.gerar_relatorio(mes_atual, mes_anterior_data)
    else:
        relatorio_data = rel_instance.gerar_relatorio(mes_atual)
    
    # Adiciona metadados
    relatorio_data["id_cliente"] = id_cliente
    relatorio_data["tipo_relatorio"] = tipo
    relatorio_data["data_geracao"] = datetime.now().isoformat()
    
    return relatorio_data

@app.get("/analise/{id_cliente}/{mes}/{ano}", 
         response_model=Dict[str, Any],
         summary="Obtém a análise qualitativa de um consultor",
         description="Recupera a análise qualitativa de um consultor para um cliente e período específico.")
def get_analise(
    id_cliente: int, 
    mes: int, 
    ano: int,
    db: DatabaseConnection = Depends(get_db)
):
    """
    Obtém a análise qualitativa (relatório 6) para um cliente e período.
    
    - **id_cliente**: ID do cliente
    - **mes**: Número do mês (1-12)
    - **ano**: Ano da análise
    """
    # Busca cliente
    clientes = buscar_clientes(db)
    cliente = next((c for c in clientes if c["id_cliente"] == id_cliente), None)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    nome_cliente = cliente["nome"]
    indicadores = Indicadores(id_cliente, db)
    relatorio6 = Relatorio6(indicadores, nome_cliente)
    mes_atual = date(ano, mes, 1)
    
    return relatorio6.gerar_relatorio(mes_atual)

@app.post("/analise/{id_cliente}/{mes}/{ano}", 
          response_model=Dict[str, Any],
          summary="Salva a análise qualitativa de um consultor",
          description="Salva a análise qualitativa de um consultor para um cliente e período específico.")
def salvar_analise(
    id_cliente: int, 
    mes: int, 
    ano: int, 
    analise: AnaliseInput,
    db: DatabaseConnection = Depends(get_db)
):
    """
    Salva uma análise qualitativa (relatório 6) para um cliente e período.
    
    - **id_cliente**: ID do cliente
    - **mes**: Número do mês (1-12)
    - **ano**: Ano da análise
    - **analise**: Texto da análise qualitativa
    """
    # Busca cliente
    clientes = buscar_clientes(db)
    cliente = next((c for c in clientes if c["id_cliente"] == id_cliente), None)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    nome_cliente = cliente["nome"]
    indicadores = Indicadores(id_cliente, db)
    relatorio6 = Relatorio6(indicadores, nome_cliente)
    mes_atual = date(ano, mes, 1)
    
    # Salva a análise
    relatorio6.salvar_analise(mes_atual, analise.analise)
    
    return {"status": "success", "message": "Análise salva com sucesso"}

@app.delete("/analise/{id_cliente}/{mes}/{ano}", 
            response_model=Dict[str, Any],
            summary="Exclui a análise qualitativa de um consultor",
            description="Exclui a análise qualitativa de um consultor para um cliente e período específico.")
def excluir_analise(
    id_cliente: int, 
    mes: int, 
    ano: int,
    db: DatabaseConnection = Depends(get_db)
):
    """
    Exclui uma análise qualitativa (relatório 6) para um cliente e período.
    
    - **id_cliente**: ID do cliente
    - **mes**: Número do mês (1-12)
    - **ano**: Ano da análise
    """
    # Busca cliente
    clientes = buscar_clientes(db)
    cliente = next((c for c in clientes if c["id_cliente"] == id_cliente), None)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    nome_cliente = cliente["nome"]
    indicadores = Indicadores(id_cliente, db)
    relatorio6 = Relatorio6(indicadores, nome_cliente)
    mes_atual = date(ano, mes, 1)
    
    # Exclui a análise
    relatorio6.excluir_analise(mes_atual)
    
    return {"status": "success", "message": "Análise excluída com sucesso"}

@app.post("/gerar-pdf", 
          response_class=FileResponse,
          summary="Gera um PDF com relatórios selecionados",
          description="Gera um arquivo PDF com os relatórios selecionados para um cliente e período.")
def gerar_pdf(
    input_data: RelatorioPdfInput,
    db: DatabaseConnection = Depends(get_db)
):
    """
    Gera um PDF com os relatórios selecionados.
    
    - **id_cliente**: ID do cliente
    - **mes**: Número do mês (1-12)
    - **ano**: Ano do relatório
    - **nome_cliente**: Nome do cliente (para o cabeçalho)
    - **relatorios**: Lista de tipos de relatórios a incluir (1-7)
    - **analise_qualitativa**: Texto opcional da análise qualitativa (relatório 6)
    """
    try:
        # Instancia serviços
        indicadores = Indicadores(input_data.id_cliente, db)
        
        # Mapeamento de classes de relatórios
        relatorios_classes = {
            1: Relatorio1,
            2: Relatorio2,
            3: Relatorio3,
            4: Relatorio4,
            5: Relatorio5,
            6: Relatorio6,
            7: Relatorio7
        }
        
        # Obtém nomes dos meses
        meses = obter_meses()
        mes_nome = next(m[0] for m in meses if m[1] == input_data.mes)
        
        # Prepara dados para geração do PDF
        relatorios_dados = []
        mes_atual = date(input_data.ano, input_data.mes, 1)
        mes_anterior = date(input_data.ano, input_data.mes - 1, 1) if input_data.mes > 1 else date(input_data.ano - 1, 12, 1)
        
        for rel_tipo in input_data.relatorios:
            rel_class = relatorios_classes[rel_tipo]
            relatorio = rel_class(indicadores, input_data.nome_cliente)
            
            # Tratamento especial para cada tipo de relatório
            if rel_tipo == 6 and input_data.analise_qualitativa:
                # Se enviou análise, salva primeiro
                relatorio.salvar_analise(mes_atual, input_data.analise_qualitativa)
                dados = relatorio.gerar_relatorio(mes_atual)
            elif rel_tipo in [1, 2, 3]:
                # Relatórios que precisam do mês anterior
                dados = relatorio.gerar_relatorio(mes_atual, mes_anterior)
            else:
                # Outros relatórios
                dados = relatorio.gerar_relatorio(mes_atual)
            
            # Nome do relatório para o PDF
            rel_nome = f"Relatório {rel_tipo} - " + {
                1: "Resultados Mensais",
                2: "Análise por Competência",
                3: "Análise de Lucros",
                4: "Evolução",
                5: "Indicadores",
                6: "Análise Qualitativa",
                7: "Imagens"
            }[rel_tipo]
            
            relatorios_dados.append((rel_nome, dados))
        
        # Gera o PDF
        pdf_gen = PDFGenerator()
        
        # Cria arquivo temporário para o PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            output_path = tmp.name
        
        pdf_file = pdf_gen.generate_pdf(
            relatorios_dados, 
            input_data.nome_cliente, 
            mes_nome, 
            input_data.ano, 
            output_path
        )
        
        # Retorna o arquivo PDF
        return FileResponse(
            path=pdf_file,
            filename=f"Relatorio_{input_data.nome_cliente.replace(' ', '_')}_{mes_nome}_{input_data.ano}.pdf",
            media_type="application/pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {str(e)}")

@app.get("/health", 
         response_model=Dict[str, str],
         summary="Verifica o status da API",
         description="Retorna o status atual da API.")
def health_check():
    """Endpoint para verificação de saúde da API."""
    return {"status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)