from typing import Dict, Any, List, Tuple, Union
from src.rendering.renderers.base_renderer import BaseRenderer
import os

class Relatorio7Renderer(BaseRenderer):
    """Renderizador específico para o Relatório 7 - Indicadores."""
    
    def render(self, data: Union[List[Dict[str, Any]], Tuple[List[Dict[str, Any]], Dict[str, str]]], 
               cliente_nome: str, mes_nome: str, ano: int) -> str:
        """
        Renderiza os indicadores operacionais.
        
        Args:
            data: Lista de dicionários ou tupla (lista_dicionarios, {"notas": notas})
            cliente_nome: Nome do cliente
            mes_nome: Nome do mês
            ano: Ano do relatório
            
        Returns:
            HTML formatado
        """
        # Verificar o formato dos dados (lista de dicionários ou tupla)
        if isinstance(data, tuple) and len(data) == 2:
            # Formato: (lista_de_indicadores, {"notas": notas})
            indicadores_data = data[0]
            notas = data[1].get("notas", "")
        else:
            # Formato: lista_de_indicadores
            indicadores_data = data
            notas = ""
            
        # Carrega o CSS diretamente do arquivo
        css_path = os.path.join("templates", "relatorio7", "style.css")
        css_content = ""
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
        # Organizar indicadores em grupos para melhor visualização
        indicadores_financeiros = []
        indicadores_vendas = []
        indicadores_clientes = []
        indicadores_outros = []
        
        for item in indicadores_data:
            categoria = item["categoria"]
            valor = item["valor"]
            
            # Categorizar indicadores
            if categoria in ["Faturamento", "Geração de Caixa", "Lucro Líquido", 
                            "Margem de Contribuição (Lucro Bruto)", 
                            "% Investimentos", "EBITDA"]:
                indicadores_financeiros.append({"nome": categoria, "valor": valor})
            elif "Ticket" in categoria or "Cliente" in categoria or "Cota" in categoria:
                indicadores_clientes.append({"nome": categoria, "valor": valor})
            elif "Venda" in categoria or "Assessor" in categoria or "Crescimento" in categoria:
                indicadores_vendas.append({"nome": categoria, "valor": valor})
            else:
                indicadores_outros.append({"nome": categoria, "valor": valor})
        
        # Ordenar indicadores por nome
        indicadores_financeiros.sort(key=lambda x: x["nome"])
        indicadores_vendas.sort(key=lambda x: x["nome"])
        indicadores_clientes.sort(key=lambda x: x["nome"])
        indicadores_outros.sort(key=lambda x: x["nome"])
        
        
        # Preparar contexto para o template
        context = {
            "cliente_nome": cliente_nome,
            "mes_nome": mes_nome,
            "ano": ano,
            "indicadores_financeiros": indicadores_financeiros,
            "indicadores_vendas": indicadores_vendas,
            "indicadores_clientes": indicadores_clientes,
            "indicadores_outros": indicadores_outros,
            "notas": notas,
            "css_content": css_content
        }
        
        # Renderizar usando o template específico
        template = self.env.get_template("relatorio7/template.html")
        return template.render(**context)