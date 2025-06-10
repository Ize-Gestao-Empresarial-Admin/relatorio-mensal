from templates_test.template_test_r5_p2 import generate_histogram_base64
from jinja2 import Template

def test_report():
    # Lê o template HTML
    with open('templates_test/render_r5_p2_test.html', 'r') as f:
        template_html = f.read()

    # Gera o gráfico
    histogram_base64 = generate_histogram_base64()

    # Renderiza o HTML
    template = Template(template_html)
    html_final = template.render(histogram_base64=histogram_base64)

    # Salva o resultado
    with open('report_output.html', 'w') as f:
        f.write(html_final)

if __name__ == "__main__":
    test_report()