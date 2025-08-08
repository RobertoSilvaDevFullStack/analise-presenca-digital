FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema necessárias para Selenium
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 5000

# Comando para executar a aplicação
CMD ["python", "app.py"]