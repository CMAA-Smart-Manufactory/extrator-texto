FROM python:3.10-slim

WORKDIR /app

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV HOME=/app

# Instalar dependências Python
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar aplicação
COPY . .

# Criar diretórios
RUN mkdir -p \
    /app/uploads \
    /app/temp \
    /app/.cache \
    /app/.EasyOCR

# Porta da API
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Inicialização
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]