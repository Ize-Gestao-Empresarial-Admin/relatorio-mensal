FROM python:3.10-slim

# Instalar dependências do sistema necessárias
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
    libssl3 \
    ca-certificates \
    xfonts-75dpi \
    xfonts-base \
    && rm -rf /var/lib/apt/lists/*

# Baixar e instalar wkhtmltopdf manualmente (versão compatível com Debian Bookworm)
RUN wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && dpkg -i wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && rm wkhtmltox_0.12.6.1-3.bookworm_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Verificar instalação do wkhtmltopdf
RUN wkhtmltopdf --version

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivo de dependências primeiro (melhor cache de Docker)
COPY requirements-api.txt ./requirements.txt

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo o código da aplicação
COPY . .

# Criar diretório de outputs com permissões corretas
RUN mkdir -p outputs && chmod 777 outputs

# Definir variável de ambiente para porta
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expor a porta
EXPOSE 8080

# Comando para iniciar a API (com healthcheck)
CMD ["python", "app.py"]