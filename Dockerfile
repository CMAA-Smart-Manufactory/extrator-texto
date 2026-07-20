FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV HOME=/app

RUN mkdir -p /app/uploads /app/temp /app/.cache /app/.EasyOCR

EXPOSE 8081

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8081"]