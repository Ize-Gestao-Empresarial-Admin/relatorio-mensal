from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from src.interfaces.graficos import Graficos

def gerar_pdf(relatorios, cliente_id, mes, ano):
    graficos = Graficos()
    fig = graficos.grafico_r1(relatorios[0], relatorios[0]["Empresa"], mes, ano)
    fig.write_image("grafico_r1.png", width=600, height=400)

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('relatorio.html')
    html_out = template.render(relatorios=relatorios, mes=mes, ano=ano)
    
    pdf_file = f"relatorio_{cliente_id}_{mes}_{ano}.pdf"
    HTML(string=html_out).write_pdf(pdf_file)
    return pdf_file