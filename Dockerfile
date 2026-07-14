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
# (curl é necessário para o HEALTHCHECK abaixo)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar Python packages do builder
COPY --from=builder /root/.local /root/.local

# Configurar PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
# HOME=/app faz o easyocr salvar os modelos baixados em /app/.EasyOCR,
# que fica dentro do volume persistente montado no docker-compose (evita
# re-baixar ~500MB de modelo a cada deploy/restart do container).
ENV HOME=/app

# Diretório de trabalho
WORKDIR /app

# Copiar código
COPY . .

# Criar diretórios necessários
RUN mkdir -p /app/uploads /app/temp /app/.cache /app/.EasyOCR

# Expor porta
EXPOSE 8000

# Healthcheck (start-period alto pois a 1ª chamada de OCR baixa os modelos,
# o que pode levar 30-60s antes de o serviço responder normalmente)
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para iniciar
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
