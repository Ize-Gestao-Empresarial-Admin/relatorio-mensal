# Comandos de execução do código

## Para rodar o STREAMLIT

`.\.venv\Scripts\Activate.ps1 & python -m streamlit run main.py`

Acessar <http://localhost:8501/embed=true?is_admin=true> para visualizar o 'front' do Streamlit que será mostrado na Plataforma IZE.

## Para rodar a API (Swagger)

`.venv\Scripts\python.exe app.py`


## Para atualizar a API após mudanças (Google Cloud)

`gcloud run deploy ize-relatorios-api --source . --region southamerica-east1`