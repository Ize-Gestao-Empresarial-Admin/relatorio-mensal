# DEVE SER REFEITA PARA REFLETIR AS ALTERACOES DAS ESTRUTURAS DOS RELATORIOS   

from fastapi import FastAPI, HTTPException, Query, Body, Response, Depends
from fastapi.responses import FileResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import date, datetime
import os
import tempfile
import logging

from src.core.indicadores import Indicadores
from src.core.relatorios.relatorio_1 import Relatorio1
from src.core.relatorios.relatorio_2 import Relatorio2
from src.core.relatorios.relatorio_3 import Relatorio3
from src.core.relatorios.relatorio_4 import Relatorio4
from src.core.relatorios.relatorio_5 import Relatorio5
from src.core.relatorios.relatorio_6 import Relatorio6
from src.core.relatorios.relatorio_7 import Relatorio7
from src.core.relatorios.relatorio_8 import Relatorio8
from src.database.db_utils import DatabaseConnection, buscar_clientes, obter_meses
from src.rendering.engine import RenderingEngine

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Relatórios Financeiros",
    description="""
    API para geração de relatórios financeiros para clientes.
    Suporta 8 tipos de relatórios que podem ser obtidos individualmente ou combinados em um PDF.
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
    relatorios: List[int] = [1, 2, 3, 4, 5, 6, 7, 8]
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
    
    - **tipo**: Tipo de relatório (1-8)
    - **id_cliente**: ID do cliente
    - **mes**: Número do mês (1-12)
    - **ano**: Ano do relatório
    - **mes_anterior**: Se deve incluir comparação com o mês anterior
    """
    # Validação básica
    if tipo < 1 or tipo > 8:
        raise HTTPException(status_code=400, detail="Tipo de relatório inválido (deve ser 1-8)")
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
        7: Relatorio7,
        8: Relatorio8
    }
    
    relatorio_class = relatorio_classes[tipo]
    rel_instance = relatorio_class(indicadores, nome_cliente)
    
    # Gera o relatório
    if tipo in [1, 2, 3, 4] and mes_anterior:
        relatorio_data = rel_instance.gerar_relatorio(mes_atual, mes_anterior_data)
    else:
        relatorio_data = rel_instance.gerar_relatorio(mes_atual)
    
    # Adiciona metadados
    if isinstance(relatorio_data, list):
        resultado = {
            "data": relatorio_data,
            "id_cliente": id_cliente,
            "tipo_relatorio": tipo,
            "data_geracao": datetime.now().isoformat()
        }
        return resultado
    elif isinstance(relatorio_data, tuple) and len(relatorio_data) == 2:
        resultado, notas = relatorio_data
        return {
            "resultado": resultado,
            "notas": notas,
            "id_cliente": id_cliente,
            "tipo_relatorio": tipo,
            "data_geracao": datetime.now().isoformat()
        }
    else:
        relatorio_data["id_cliente"] = id_cliente
        relatorio_data["tipo_relatorio"] = tipo
        relatorio_data["data_geracao"] = datetime.now().isoformat()
        return relatorio_data

@app.get("/relatorios-completos/{id_cliente}/{mes}/{ano}", 
         response_model=Dict[str, Any],
         summary="Obtém todos os relatórios de uma vez",
         description="Gera todos os relatórios financeiros para um cliente, mês e ano específicos.")
def get_relatorios_completos(
    id_cliente: int, 
    mes: int, 
    ano: int, 
    mes_anterior: bool = Query(True, description="Incluir comparação com mês anterior"),
    db: DatabaseConnection = Depends(get_db)
):
    """
    Gera todos os relatórios financeiros para um cliente, mês e ano específicos.
    
    - **id_cliente**: ID do cliente
    - **mes**: Número do mês (1-12)
    - **ano**: Ano do relatório
    - **mes_anterior**: Se deve incluir comparação com o mês anterior para relatórios aplicáveis
    
    Retorna um objeto contendo todos os 8 tipos de relatórios disponíveis.
    """
    # Validação básica
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
    
    # Mapeamento de classes de relatórios
    relatorios_classes = {
        1: Relatorio1,
        2: Relatorio2,
        3: Relatorio3,
        4: Relatorio4,
        5: Relatorio5,
        6: Relatorio6,
        7: Relatorio7,
        8: Relatorio8
    }
    
    # Para armazenar os resultados
    resultados = {}
    
    # Gera cada relatório
    for tipo, relatorio_class in relatorios_classes.items():
        rel_instance = relatorio_class(indicadores, nome_cliente)
        
        # Gera o relatório com base no tipo
        if tipo in [1, 2, 3, 4] and mes_anterior:
            relatorio_data = rel_instance.gerar_relatorio(mes_atual, mes_anterior_data)
        else:
            relatorio_data = rel_instance.gerar_relatorio(mes_atual)
        
        # Nome do relatório para o resultado
        nome_relatorio = {
            1: "fluxo_caixa_receitas_custos",
            2: "fluxo_caixa_lucro_bruto_despesas",
            3: "fluxo_caixa_lucro_operacional_investimentos",
            4: "fluxo_caixa_lucro_liquido_entradas",
            5: "fluxo_caixa_fechamento",
            6: "dre_gerencial",
            7: "indicadores",
            8: "parecer_tecnico"
        }[tipo]
        
        # Adiciona ao dicionário de resultados
        resultados[nome_relatorio] = relatorio_data
    
    # Adiciona metadados
    resultados["id_cliente"] = id_cliente
    resultados["nome_cliente"] = nome_cliente
    resultados["mes"] = mes
    resultados["ano"] = ano
    resultados["data_geracao"] = datetime.now().isoformat()
    
    return resultados

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
    Obtém a análise qualitativa (relatório 8) para um cliente e período.
    
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
    relatorio8 = Relatorio8(indicadores, nome_cliente)
    mes_atual = date(ano, mes, 1)
    
    return relatorio8.gerar_relatorio(mes_atual)

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
    Salva uma análise qualitativa (relatório 8) para um cliente e período.
    
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
    relatorio8 = Relatorio8(indicadores, nome_cliente)
    mes_atual = date(ano, mes, 1)
    
    # Salva a análise
    relatorio8.salvar_analise(mes_atual, analise.analise)
    
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
    Exclui uma análise qualitativa (relatório 8) para um cliente e período.
    
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
    relatorio8 = Relatorio8(indicadores, nome_cliente)
    mes_atual = date(ano, mes, 1)
    
    # Exclui a análise
    relatorio8.excluir_analise(mes_atual)
    
    return {"status": "success", "message": "Análise excluída com sucesso"}

@app.post("/gerar-pdf", 
          response_class=FileResponse,
          summary="Gera um PDF com relatórios selecionados",
          description="Gera um arquivo PDF com os relatórios selecionados para um cliente e período.")
def gerar_pdf(
    input_data: RelatorioPdfInput,
    db: DatabaseConnection = Depends(get_db)
):
    """Gera um PDF com os relatórios selecionados usando processamento paralelo."""
    import time
    start_time = time.time()
    
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
            7: Relatorio7,
            8: Relatorio8
        }
        
        # Obtém nomes dos meses
        meses = obter_meses()
        mes_nome = next(m[0] for m in meses if m[1] == input_data.mes)
        
        # Prepara dados para geração do PDF
        relatorios_dados = []
        mes_atual = date(input_data.ano, input_data.mes, 1)
        mes_anterior = date(input_data.ano, input_data.mes - 1, 1) if input_data.mes > 1 else date(input_data.ano - 1, 12, 1)
        
        # Adicionar dados do índice
        indice_data = {
            "fluxo_caixa": "Sim" if any(r in input_data.relatorios for r in [1, 2, 3, 4, 5]) else "Não",
            "dre_gerencial": "Sim" if 6 in input_data.relatorios else "Não",
            "indicador": "Sim" if 7 in input_data.relatorios else "Não",
            "nota_consultor": "Sim" if 8 in input_data.relatorios else "Não",
            "cliente_nome": input_data.nome_cliente,
            "mes": mes_nome,
            "ano": input_data.ano,
            "nome": f"{input_data.nome_cliente}",
            "Periodo": f"{mes_nome} {input_data.ano}",
            "marca": "Sim"
        }
        relatorios_dados.append(("Índice", indice_data))
        
        for rel_tipo in input_data.relatorios:
            rel_class = relatorios_classes[rel_tipo]
            relatorio = rel_class(indicadores, input_data.nome_cliente)
            
            # Tratamento especial para cada tipo de relatório
            if rel_tipo == 8 and input_data.analise_qualitativa:
                # Se enviou análise, salva primeiro
                relatorio.salvar_analise(mes_atual, input_data.analise_qualitativa)
                dados = relatorio.gerar_relatorio(mes_atual)
            elif rel_tipo in [1, 2, 3, 4]:
                # Relatórios que precisam do mês anterior
                dados = relatorio.gerar_relatorio(mes_atual, mes_anterior)
            else:
                # Outros relatórios
                dados = relatorio.gerar_relatorio(mes_atual)
            
            # Nome do relatório para o PDF
            rel_nome = f"Relatório {rel_tipo} - " + {
                1: "Análise de Fluxo de Caixa (Receitas e Custos Variáveis)",
                2: "Análise de Fluxo de Caixa (Lucro Bruto e Despesas Fixas)",
                3: "Análise de Fluxo de Caixa (Lucro Operacional e Investimentos)",
                4: "Análise de Fluxo de Caixa (Lucro Líquido e Entradas Não Operacionais)",
                5: "Fechamento de Análise de Fluxo de Caixa",
                6: "Análise por Competência - DRE",
                7: "Indicadores",
                8: "Parecer Técnico"
            }[rel_tipo]
            
            relatorios_dados.append((rel_nome, dados))
        
        # Gera o PDF usando processamento paralelo
        rendering_engine = RenderingEngine(max_workers=4)  # Ajuste conforme necessário
        
        # Cria arquivo temporário para o PDF
        output_filename = f"Relatorio_{input_data.nome_cliente.replace(' ', '_')}_{mes_nome}_{input_data.ano}.pdf"
        output_path = os.path.join("outputs", output_filename)
        
        os.makedirs("outputs", exist_ok=True)
        
        pdf_file = rendering_engine.render_to_pdf(
            relatorios_dados, 
            input_data.nome_cliente, 
            mes_nome, 
            input_data.ano, 
            output_path
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        logger.info(f"PDF gerado em {processing_time:.2f} segundos")
        
        # Retorna o arquivo PDF
        return FileResponse(
            path=pdf_file,
            filename=output_filename,
            media_type="application/pdf"
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {str(e)}")
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