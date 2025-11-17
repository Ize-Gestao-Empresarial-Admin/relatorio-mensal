# Comandos de execução do código

## Para rodar o STREAMLIT

`.\.venv\Scripts\Activate.ps1 & python -m streamlit run main.py`

Acessar <http://localhost:8501/embed=true?is_admin=true> para visualizar o 'front' do Streamlit que será mostrado na Plataforma IZE.

**Nota:** O Streamlit agora consome a API em nuvem para gerar PDFs, não gerando mais localmente.

## Para rodar a API (Swagger) - Local

`.venv\Scripts\python.exe app.py`

## Para atualizar a API após mudanças (Google Cloud)

`gcloud run deploy ize-relatorios-api --source . --region southamerica-east1`

## API em Produção

**URL Base:** `https://ize-relatorios-api-1052359947797.southamerica-east1.run.app`

**Documentação Swagger:** `https://ize-relatorios-api-1052359947797.southamerica-east1.run.app/docs`

**API Key:** `tj8DbJ0bDYDwqLKhF4rEDKaoOW6KxIC6ofeDtc44aA_0XlOEZcu49zAQKYylodOZ`

## Para testar geração de PDF via API (Python)

```python
import requests

url = "https://ize-relatorios-api-1052359947797.southamerica-east1.run.app/v1/relatorios/pdf"
headers = {"X-API-Key": "tj8DbJ0bDYDwqLKhF4rEDKaoOW6KxIC6ofeDtc44aA_0XlOEZcu49zAQKYylodOZ"}
payload = {
    "id_cliente": [295],
    "mes": 10,
    "ano": 2025,
    "relatorios": [7, 8],
    "analise_text": "teste"
}

response = requests.post(url, json=payload, headers=headers, timeout=600)

if response.status_code == 200:
    with open("relatorio.pdf", "wb") as f:
        f.write(response.content)
    print("✅ PDF salvo: relatorio.pdf")
else:
    print(f"❌ Erro: {response.status_code}")
    print(response.text)
```