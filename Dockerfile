FROM python:3.10-slim

# Instalar dependências do sistema e wkhtmltopdf
RUN apt-get update && apt-get install -y \
    wget \
    xvfb \
    libfontconfig1 \
    libxrender1 \
    libxext6 \
    fontconfig \
    libjpeg62-turbo \
    libx11-6 \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

# Baixar e instalar wkhtmltopdf manualmente
RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && apt-get update \
    && apt-get install -y ./wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivo de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código da aplicação
COPY . .

# Criar diretório de outputs
RUN mkdir -p outputs

# Definir variável de ambiente para porta
ENV PORT=8080

# Expor a porta
EXPOSE 8080

# Comando para iniciar a API
CMD ["python", "app.py"]