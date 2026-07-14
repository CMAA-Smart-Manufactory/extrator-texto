# Documentação da API FastAPI

## Visão Geral

A API FastAPI fornece uma interface HTTP para extração de texto de múltiplos formatos de arquivo (PDF, imagens com OCR, planilhas Excel). O servidor processa arquivos enviados e retorna o texto extraído em diferentes formatos: bruto, estruturado e limpo.

## Tecnologias

- **FastAPI**: Framework web de alta performance
- **Uvicorn**: Servidor ASGI
- **Python 3.9+**: Linguagem de programação

## Instalação

### 1. Dependências

Instale todas as dependências incluindo a API:

```bash
pip install -r requirements.txt
```

As principais dependências para a API são:
- `fastapi==0.104.1` - Framework web
- `uvicorn[standard]==0.24.0` - Servidor ASGI
- `python-multipart==0.0.6` - Suporte a multipart form data

### 2. Iniciar o servidor

#### Modo desenvolvimento (com auto-reload):

```bash
python api.py
```

#### Modo produção:

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

O servidor estará disponível em: `http://localhost:8000`

## Documentação Interativa

A API fornece documentação interativa através do Swagger UI:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### 1. GET `/`

Informações gerais sobre a API.

**Response:**

```json
{
  "name": "Leitor de Arquivos API",
  "version": "1.0.0",
  "description": "API para extração de texto de documentos",
  "endpoints": {
    "health": "/health",
    "formats": "/formats",
    "extract": "/extract",
    "docs": "/docs",
    "redoc": "/redoc"
  },
  "supported_formats": [".jpeg", ".jpg", ".pdf", ".png", ".xlsx", ".xlsm"]
}
```

### 2. GET `/health`

Verifica a saúde da API e retorna formatos suportados.

**Response:**

```json
{
  "status": "ok",
  "supported_formats": [".jpeg", ".jpg", ".pdf", ".png", ".xlsx", ".xlsm"]
}
```

### 3. GET `/formats`

Retorna a lista de formatos de arquivo suportados.

**Response:**

```json
{
  "supported_formats": [".jpeg", ".jpg", ".pdf", ".png", ".xlsx", ".xlsm"],
  "description": "Formatos de arquivo que podem ser processados"
}
```

### 4. POST `/extract`

**Principal endpoint para extração de texto.**

Extrai texto de um arquivo enviado. O arquivo é processado para extrair:
- **Texto bruto**: concatenação simples do texto encontrado
- **Texto estruturado**: preservando layout/estrutura
- **Texto limpo**: versão otimizada para leitura

#### Request

```bash
curl -X POST http://localhost:8000/extract \
  -F "file=@/caminho/para/arquivo.pdf"
```

#### Parameters

| Parâmetro | Tipo | Descrição | Obrigatório |
|-----------|------|-----------|------------|
| `file` | File | Arquivo a processar (PDF, PNG, JPG, JPEG, XLSX, XLSM) | Sim |

#### Response (Success - 200)

```json
{
  "success": true,
  "filename": "documento.pdf",
  "file_extension": ".pdf",
  "raw_text": "Texto bruto extraído...",
  "structured_text": "Texto estruturado preservando layout...",
  "cleaned_text": "Texto limpo e formatado...",
  "message": "Arquivo processado com sucesso"
}
```

#### Response (Error - 400)

```json
{
  "detail": "Formato '.doc' não suportado. Formatos suportados: ['.jpeg', '.jpg', '.pdf', '.png', '.xlsx', '.xlsm']"
}
```

#### Response (Error - 500)

```json
{
  "detail": "Erro interno ao processar arquivo: mensagem de erro específica"
}
```

### 5. POST `/extract-debug`

Endpoint de debug com informações adicionais sobre o processamento.

#### Response (Success - 200)

```json
{
  "success": true,
  "filename": "documento.pdf",
  "file_extension": ".pdf",
  "file_size": 1024000,
  "raw_text_length": 5432,
  "structured_text_length": 5876,
  "raw_text": "Texto bruto...",
  "structured_text": "Texto estruturado...",
  "cleaned_text": "Texto limpo..."
}
```

## Exemplos de Uso

### Python com `requests`

```python
import requests

# Arquivo PDF
with open('documento.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/extract', files=files)
    
result = response.json()

if result['success']:
    print("Texto extraído:")
    print(result['cleaned_text'])
else:
    print(f"Erro: {result['error']}")
```

### cURL

```bash
# Extrair texto de um PDF
curl -X POST http://localhost:8000/extract \
  -F "file=@documento.pdf"

# Extrair texto de uma imagem
curl -X POST http://localhost:8000/extract \
  -F "file=@recibo.jpg"

# Extrair texto de uma planilha
curl -X POST http://localhost:8000/extract \
  -F "file=@dados.xlsx"
```

### JavaScript/Fetch

```javascript
// Extrair texto usando Fetch API
async function extractText(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:8000/extract', {
    method: 'POST',
    body: formData
  });

  const result = await response.json();
  
  if (result.success) {
    console.log('Texto extraído:');
    console.log(result.cleaned_text);
  } else {
    console.error('Erro:', result.error);
  }
}

// Uso
const fileInput = document.querySelector('input[type="file"]');
fileInput.addEventListener('change', (e) => {
  extractText(e.target.files[0]);
});
```

### HTML Form

```html
<!DOCTYPE html>
<html>
<head>
    <title>Extrator de Texto</title>
</head>
<body>
    <h1>Upload de Arquivo</h1>
    <form id="uploadForm">
        <input type="file" id="fileInput" accept=".pdf,.png,.jpg,.jpeg,.xlsx,.xlsm" required>
        <button type="submit">Extrair Texto</button>
    </form>
    
    <div id="result"></div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const file = document.getElementById('fileInput').files[0];
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/extract', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('result').innerHTML = `
                        <h2>Resultado</h2>
                        <h3>Arquivo: ${result.filename}</h3>
                        <h4>Texto Limpo:</h4>
                        <pre>${result.cleaned_text}</pre>
                    `;
                } else {
                    document.getElementById('result').innerHTML = `
                        <h2>Erro</h2>
                        <p>${result.error}</p>
                    `;
                }
            } catch (error) {
                document.getElementById('result').innerHTML = `
                    <h2>Erro na Requisição</h2>
                    <p>${error.message}</p>
                `;
            }
        });
    </script>
</body>
</html>
```

## Formatos Suportados

### Imagens (OCR com português)

- `.png` - PNG com OCR
- `.jpg` - JPEG com OCR  
- `.jpeg` - JPEG com OCR

**Processamento**: Usa easyocr com modelo português. Extrai texto preservando layout aproximado.

### Documentos

- `.pdf` - PDF digital

**Processamento**: Extrai texto das páginas preservando estrutura em blocos.

### Planilhas

- `.xlsx` - Excel moderno
- `.xlsm` - Excel com macros

**Processamento**: Lê células e alinha colunas em formato texto.

## Códigos de Status HTTP

| Código | Significado | Descrição |
|--------|-------------|-----------|
| 200 | OK | Requisição bem-sucedida |
| 400 | Bad Request | Arquivo inválido ou formato não suportado |
| 422 | Unprocessable Entity | Nenhum arquivo foi enviado |
| 500 | Internal Server Error | Erro ao processar arquivo |

## Tratamento de Erros

A API retorna erros estruturados em formato JSON:

```json
{
  "detail": "Mensagem de erro descritiva"
}
```

### Cenários de Erro Comuns

**1. Formato não suportado:**
```
Formato '.doc' não suportado. Formatos suportados: [...]
```

**2. Arquivo corrompido:**
```
Não foi possível ler a imagem: caminho/do/arquivo.jpg
```

**3. Arquivo não enviado:**
```
Nome de arquivo inválido
```

## Modelos de Dados

### TextExtractionResponse

```python
{
    "success": bool,              # Sucesso da operação
    "filename": str,              # Nome do arquivo processado
    "file_extension": str,        # Extensão do arquivo
    "raw_text": str,              # Texto bruto concatenado
    "structured_text": str,       # Texto preservando estrutura
    "cleaned_text": str,          # Texto limpo e formatado
    "message": str                # Mensagem de status
}
```

### HealthResponse

```python
{
    "status": str,                # Status da API
    "supported_formats": list[str] # Formatos suportados
}
```

## Arquitetura

```
api.py
├── FastAPI App
├── CORS Middleware
├── Routes
│   ├── GET /
│   ├── GET /health
│   ├── GET /formats
│   ├── POST /extract
│   └── POST /extract-debug
└── Models (Pydantic)
    ├── TextExtractionResponse
    ├── ErrorResponse
    └── HealthResponse

processor.py
├── extract_text(file_path)
├── extract_text_from_pdf(file_path)
├── extract_text_from_image(file_path)
├── extract_text_from_excel(file_path)
├── clean_text_for_reading(text)
├── get_supported_formats()
└── is_supported_format(extension)
```

## Configuração de Produção

### Com Gunicorn + Uvicorn

```bash
pip install gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Com Docker

```dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t leitor-api .
docker run -p 8000:8000 leitor-api
```

### Com Nginx (Reverse Proxy)

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Desempenho

- **Processamento de PDFs simples**: ~1-2 segundos
- **OCR em imagens**: ~5-10 segundos (dependendo do tamanho)
- **Planilhas**: ~500ms-2 segundos

**Recomendações:**

- Use limite de tamanho de arquivo (~50MB)
- Implemente timeout de 60 segundos para requisições
- Use cache para arquivos idênticos
- Implemente fila de processamento para múltiplas requisições simultâneas

## Segurança

### Recomendações de Deploy

1. **Validação de arquivo**: Sempre valide tipo e tamanho
2. **Rate limiting**: Implemente limite de requisições por IP
3. **Autenticação**: Adicione API Key ou OAuth para produção
4. **HTTPS**: Use certificado SSL em produção
5. **CORS**: Configure origins específicas em produção

### Exemplo com Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/extract")
@limiter.limit("5/minute")
async def extract_file(request: Request, file: UploadFile = File(...)):
    # ... resto do código
```

## Resolução de Problemas

### A API não inicia

```bash
# Verificar porta 8000 em uso
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Usar porta diferente
uvicorn api:app --port 8001
```

### Erro "Não foi possível ler a imagem"

- Verifique se a imagem está corrompida
- Tente converter para PNG
- Verifique permissões de leitura do arquivo

### Erro de OCR em português

- O modelo português é baixado na primeira execução
- Verifique conexão com internet na primeira execução
- Modelo é armazenado em cache local

### Out of Memory

- Reduza tamanho máximo de arquivo aceito
- Implemente processamento em chunks
- Use limite de workers

## Suporte e Contribuições

Para relatar problemas ou sugerir melhorias, contacte o desenvolvedor ou abra uma issue no repositório.

## Changelog

### v1.0.0

- ✅ Suporte para PDF, imagens (OCR), planilhas Excel
- ✅ API FastAPI com documentação automática
- ✅ Múltiplos formatos de saída (bruto, estruturado, limpo)
- ✅ CORS habilitado
- ✅ Endpoint de health check
- ✅ Endpoint de debug
