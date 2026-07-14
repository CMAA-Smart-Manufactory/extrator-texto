# Documentação Técnica

## Visão Geral

Este projeto extrai texto de documentos (notas fiscais, recibos, planilhas) com duas interfaces:

1. **CLI (main.py)** - Interface de linha de comando para uso local
2. **API (api.py)** - Interface REST com FastAPI para consumo remoto

O processamento é 100% local sem dependência de APIs externas.

## Arquitetura Geral

```
┌─────────────────────────────────────────────────┐
│                  Cliente/Usuário                 │
│          (CLI, Web, Mobile, Desktop)             │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
    CLI │                     │ HTTP
  (main.py)               (api.py)
        │                     │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  processor.py       │
        │  (Núcleo)           │
        │                     │
        │ - extract_text()    │
        │ - clean_text()      │
        │ - validate()        │
        └─────────┬────────┬──┘
                  │        │
        ┌─────────▼──┐   ┌─▼────────┐
        │ Libraries  │   │ Temp Dir │
        │            │   │ Storage  │
        │ - fitz     │   │          │
        │ - cv2      │   │ Upload   │
        │ - easyocr  │   │ files    │
        │ - openpyxl │   │          │
        └────────────┘   └──────────┘
```

## Modularização

### 1. `processor.py` - Núcleo de Processamento

Contém toda a lógica de extração e processamento:

```python
# Funções principais
extract_text(file_path)                    # Dispatcher principal
extract_text_from_pdf(file_path)          # Extração PDF
extract_text_from_image(file_path)        # OCR com easyocr
extract_text_from_excel(file_path)        # Leitura planilha
clean_text_for_reading(text)              # Limpeza de texto
is_supported_format(file_extension)       # Validação
get_supported_formats()                   # Lista de formatos

# Constantes
SUPPORTED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.xlsx', '.xlsm'}
```

**Retorno de funções de extração:**

```python
Retorna: Tuple[str, str]
├── [0] raw_text: Concatenação simples
└── [1] structured_text: Layout preservado
```

### 2. `main.py` - Interface CLI

Interface de linha de comando que:
- Valida argumentos
- Gerencia diretórios
- Processa múltiplos arquivos
- Exibe resultados no console

**Fluxo:**

```
Argumentos
    ↓
Validar caminho
    ↓
├─ Se arquivo: processar
└─ Se pasta: listar e processar
    ↓
Para cada arquivo:
  - extract_text()
  - clean_text_for_reading()
  - print() no console
    ↓
Tratamento de erros
```

### 3. `api.py` - API FastAPI

Interface HTTP que:
- Recebe uploads de arquivo
- Processa usando processor.py
- Retorna JSON estruturado
- Oferece documentação interativa

**Endpoints:**

```
GET  /              → Informações da API
GET  /health        → Verificação de saúde
GET  /formats       → Formatos suportados
POST /extract       → Extração principal
POST /extract-debug → Debug com detalhes
```

## Fluxo de Processamento

### Fluxo CLI

```
python main.py arquivo.pdf
     ↓
ArgumentParser valida caminho
     ↓
Verifica se arquivo/pasta existe
     ↓
Para cada arquivo:
  ├─ extract_text(file_path)
  │  ├─ Valida extensão
  │  ├─ Chama função específica
  │  └─ Retorna (raw, structured)
  │
  ├─ clean_text_for_reading(texto)
  │  ├─ Normaliza espaços
  │  ├─ Remove linhas vazias
  │  └─ Agrupa linhas curtas
  │
  └─ print(cleaned_text)
     ↓
Tratamento de erros captura exceções
```

### Fluxo API

```
POST /extract + file
     ↓
FastAPI recebe multipart/form-data
     ↓
Salvar em arquivo temporário
     ↓
Validar extensão
     ↓
extract_text(temp_file)
├─ Retorna (raw, structured)
└─ Detecta formato e escolhe processador
     ↓
clean_text_for_reading()
     ↓
Montar TextExtractionResponse JSON
     ↓
Deletar arquivo temporário
     ↓
Retornar 200 OK + JSON
     ├─ ou 400 Bad Request
     └─ ou 500 Internal Server Error
```

## Processamento por Formato

### PDF (`.pdf`)

**Bibliotecas:** PyMuPDF (fitz)

**Algoritmo:**

```
1. fitz.open(file_path)
2. Para cada página:
   a) page.get_text("text") → raw_text
   b) page.get_text("blocks") → [x0, y0, x1, y1, text]
   c) Ordenar blocos por posição (y, x)
   d) Aplicar indentação baseada em x0
   e) Juntar em page_lines
3. Concatenar todas as páginas
```

**Entrada:**
```
documento.pdf (arquivo binário)
```

**Saída:**
```python
raw_text = "Página 1 conteúdo\nPágina 2 conteúdo..."
structured_text = "Texto preservando layout:\n    Indentado\n        Mais indentado"
```

### Imagens (`.png`, `.jpg`, `.jpeg`)

**Bibliotecas:** OpenCV (cv2), EasyOCR

**Algoritmo:**

```
1. cv2.imread(image_path) → numpy array
2. easyocr.Reader(['pt']).readtext(image) → [(bbox, text, conf), ...]
3. Para cada resultado:
   a) Extrair bbox: [[x0,y0], [x1,y1], [x2,y2], [x3,y3]]
   b) Calcular cy (center-y) para agrupar em linhas
   c) Armazenar (x0, x1, cy, text)
4. Agrupar em linhas (ordenar por cy com threshold)
5. Dentro de cada linha, ordenar por x0 (esquerda para direita)
6. Aplicar espaçamento entre elementos
```

**Entrada:**
```
recibo.jpg (imagem JPEG)
```

**Saída:**
```python
raw_text = "Linha 1\nLinha 2\nLinha 3"
structured_text = "Preserva posição:
    Indentado à direita
Voltou à esquerda"
```

**Problemas Comuns:**
- Imagens inclinadas: pré-processar com rotação
- Qualidade baixa: easyocr é robusto mas tem limite
- Idioma: modelo está configurado para português ('pt')

### Excel (`.xlsx`, `.xlsm`)

**Bibliotecas:** openpyxl

**Algoritmo:**

```
1. openpyxl.load_workbook(file, data_only=True)
2. Para cada sheet:
   a) sheet.iter_rows(values_only=True)
   b) Filtrar células vazias
   c) raw_text: juntar com espaço
   d) structured_text: alinhar colunas
      - Calcular max width por coluna
      - Usar ljust(width) para alinhamento
      - Separar com ' | '
3. Juntar todas as sheets
```

**Entrada:**
```
dados.xlsx (arquivo Excel)
```

**Saída:**
```python
raw_text = "## Planilha: Sheet1\nColuna1 Coluna2 Coluna3..."
structured_text = "## Planilha: Sheet1
Coluna1 | Coluna2     | Coluna3
Dado1   | DadoComMais | Dado3"
```

## Limpeza de Texto

**Função:** `clean_text_for_reading(text: str) -> str`

**Etapas:**

```
1. Dividir por linhas
2. Normalizar espaços: re.sub(r"\s+", " ", line) → múltiplos espaços → 1 espaço
3. Strip() cada linha → remover espaços laterais
4. Filtrar linhas vazias
5. Mesclar linhas curtas:
   - Se linha atual tem < 40 caracteres
   - E próxima linha tem < 80 caracteres
   - Juntar com espaço
6. Juntar com \n
```

**Exemplo:**

```
Entrada:
"Empresa   X\n\n\nNota   Fiscal\n\nData: 01/01\nValor: 1000"

Depois normalizar:
"Empresa X"
"Nota Fiscal"
"Data: 01/01"
"Valor: 1000"

Depois mesclar curtas:
"Empresa X Nota Fiscal"
"Data: 01/01 Valor: 1000"

Saída:
"Empresa X Nota Fiscal\nData: 01/01 Valor: 1000"
```

## Tratamento de Erros

**Hierarquia de erros:**

```
Exception
├── ValueError (Formato não suportado, arquivo corrompido)
│   └── Capturado em extract_text()
├── FileNotFoundError (Arquivo não existe)
│   └── Capturado em main.py validação
└── (Qualquer outro erro)
    └── Capturado como Internal Server Error na API
```

**CLI (main.py):**

```python
try:
    raw_text, structured_text = extract_text(file_path)
except Exception as exc:
    print(f"Erro ao processar o arquivo: {exc}")
    # Continua para próximo arquivo
```

**API (api.py):**

```python
try:
    raw_text, structured_text = extract_text(temp_file_path)
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
finally:
    # Sempre limpar arquivo temporário
    if temp_file_path and os.path.exists(temp_file_path):
        os.unlink(temp_file_path)
```

## Gestão de Arquivos Temporários

**API:**

```
Upload → tempfile.NamedTemporaryFile
          ├─ Caminho: /tmp/upload_*.pdf (ou outro ext)
          ├─ delete=False (manual cleanup)
          └─ Processamento
              ↓
         Resultado JSON
              ↓
         os.unlink(temp_file)
          ├─ Sucesso → deleta
          └─ Erro → try/except → deleta anyway
```

**CLI:**

- Não cria temporários
- Processa arquivo original in-place
- Apenas lê, não modifica

## Performance

### Benchmarks

```
┌─────────────────────────────────────────┐
│ Operação              │ Tempo Típico    │
├─────────────────────────────────────────┤
│ PDF (5 páginas)       │ 1-2 segundos    │
│ Imagem (2048x1536)    │ 5-10 segundos   │
│ Imagem (512x384)      │ 2-3 segundos    │
│ Excel (100 linhas)    │ 500ms - 1s      │
│ Inicialização (1x)    │ 30-60 segundos* │
│ Requisição (cache)    │ 10-50ms         │
└─────────────────────────────────────────┘

*Apenas na primeira execução (download modelos OCR)
```

### Otimizações

**OCR (easyocr):**
- Modelo português ~500MB baixado uma vez
- GPU se disponível (gpu=True)
- Cache em ~/.EasyOCR/model_cache

**PDF (PyMuPDF):**
- Processamento por página é rápido
- Limite de blocos lineares por página

**Excel (openpyxl):**
- data_only=True já carrega valores
- Sem processamento de fórmulas

## Extensibilidade

### Adicionar Novo Formato

```python
# 1. Adicionar em SUPPORTED_EXTENSIONS
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.png', '.jpg', '.xlsx', '.xlsm'}

# 2. Criar função extract_text_from_docx()
def extract_text_from_docx(file_path: str) -> tuple[str, str]:
    from docx import Document
    doc = Document(file_path)
    raw_text = '\n'.join([p.text for p in doc.paragraphs])
    return raw_text, raw_text

# 3. Adicionar case em extract_text()
if extension == '.docx':
    return extract_text_from_docx(file_path)
```

### Melhorias Futuras

```
Priority | Feature
---------|-----------------------------------------------------------
P0       | Rate limiting na API
P0       | Autenticação/API Key
P1       | Fila de processamento para múltiplos arquivos
P1       | Cache de resultados com hash do arquivo
P1       | Extração de dados estruturados (entidades)
P2       | Suporte DOCX/RTF
P2       | Interface web
P3       | Webhook para notificação de conclusão
```

## Configuração para Produção

### Variáveis de Ambiente

```bash
# .env
OCR_LANGUAGE=pt          # Idioma OCR
MAX_FILE_SIZE=52428800   # 50MB
TEMP_DIR=/tmp/leitor     # Diretório temporário
API_WORKERS=4            # Workers Uvicorn
API_PORT=8000            # Porta
API_HOST=0.0.0.0         # Host
```

### Docker

```dockerfile
FROM python:3.10-slim

RUN apt-get update && apt-get install -y libsm6 libxext6

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.example.com;
    client_max_body_size 50M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

## Testes Recomendados

```python
# test_processor.py
import pytest
from processor import extract_text, is_supported_format

def test_pdf_extraction():
    raw, struct = extract_text('test.pdf')
    assert len(raw) > 0

def test_image_extraction():
    raw, struct = extract_text('test.jpg')
    assert len(raw) > 0

def test_excel_extraction():
    raw, struct = extract_text('test.xlsx')
    assert len(raw) > 0

def test_unsupported_format():
    with pytest.raises(ValueError):
        extract_text('file.doc')

def test_supported_formats():
    assert is_supported_format('.pdf')
    assert is_supported_format('.jpg')
    assert not is_supported_format('.doc')
```

## Limitações Conhecidas

1. **OCR português** - Dependente de qualidade de imagem
2. **Layout complexo** - Pode não preservar totalmente em imagens
3. **PDFs scaneados** - Requerem OCR (mais lento)
4. **Planilhas** - Não processa fórmulas, apenas valores
5. **Tamanho arquivo** - Sem limite hard, mas prático ~100MB

## Referências

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [PyMuPDF](https://pymupdf.readthedocs.io)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [OpenCV](https://docs.opencv.org)
- [openpyxl](https://openpyxl.readthedocs.io)
- A limpeza de texto visa legibilidade, não fidelidade exata ao documento.

## Possíveis melhorias futuras

- Exportação do texto extraído para arquivos `.txt`.
- Inserção de um modo de extração direta de dados (CNPJ, valores, quantidades) quando precisar de análise estruturada.
- Suporte a mais formatos, como `.csv`, `.tiff` e `.docx`.
- Interface CLI mais rica com opções de saída e filtros.
