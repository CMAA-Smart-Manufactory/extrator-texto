# Multi-stage build para otimizar tamanho da imagem
FROM python:3.10-slim as builder

# Instalar dependências de sistema necessárias para build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Criar wheels das dependências
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# Stage final
FROM python:3.10-slim

# Instalar dependências de sistema necessárias para runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar Python packages do builder
COPY --from=builder /root/.local /root/.local

# Configurar PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho
WORKDIR /app

# Copiar código
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/uploads /app/temp /app/.cache

# Expor porta
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Comando para iniciar
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
