# 📖 Guia Completo: Entendendo o `client.py`

O `client.py` é um **cliente Python que se conecta à API FastAPI** para extrair texto de arquivos. Ele funciona como um intermediário entre você e a API.

---

## 🏗️ Estrutura

O arquivo tem **2 partes principais**:

### 1️⃣ **Classe `ExtractorClient`** (linhas 8-98)

É uma classe que encapsula todas as operações com a API.

#### 🔧 **`__init__(base_url)`** - Inicialização

```python
def __init__(self, base_url: str = "http://localhost:8000"):
    self.base_url = base_url.rstrip("/")
    self.session = requests.Session()
```

**O que faz:**
- Define a URL da API (padrão: `http://localhost:8000`)
- Cria uma `session` do requests para reutilizar conexões (mais eficiente)

**Exemplo de uso:**
```python
client = ExtractorClient()  # Usa localhost
# ou
client = ExtractorClient("http://seu-servidor.com:8000")  # Usa outro servidor
```

---

#### ✅ **`health_check()`** - Verificar se API está viva

```python
def health_check(self) -> dict:
    response = self.session.get(f"{self.base_url}/health")
    response.raise_for_status()
    return response.json()
```

**O que faz:**
- Faz requisição `GET /health` à API
- Retorna um dicionário com status e formatos suportados

**Exemplo:**
```python
client = ExtractorClient()
health = client.health_check()
print(health)
# Output: {'status': 'ok', 'supported_formats': ['.pdf', '.jpg', '.png', ...]}
```

---

#### 📋 **`get_supported_formats()`** - Listar formatos

```python
def get_supported_formats(self) -> list[str]:
    response = self.session.get(f"{self.base_url}/formats")
    response.raise_for_status()
    data = response.json()
    return data.get("supported_formats", [])
```

**O que faz:**
- Faz requisição `GET /formats` à API
- Retorna lista de extensões suportadas

**Exemplo:**
```python
client = ExtractorClient()
formats = client.get_supported_formats()
print(formats)
# Output: ['.pdf', '.jpg', '.jpeg', '.png', '.xlsx', '.xlsm']
```

---

#### 🚀 **`extract_text(file_path)`** - Extrair texto (principal)

```python
def extract_text(self, file_path: str) -> dict:
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    with open(file_path_obj, "rb") as f:
        files = {"file": (file_path_obj.name, f)}
        response = self.session.post(f"{self.base_url}/extract", files=files)

    response.raise_for_status()
    return response.json()
```

**O que faz:**
1. Verifica se arquivo existe
2. Abre arquivo em modo binário (`rb`)
3. Faz requisição `POST /extract` com o arquivo
4. Retorna dicionário com textos extraídos

**Retorno:**
```python
{
    "success": True,
    "filename": "documento.pdf",
    "file_extension": ".pdf",
    "raw_text": "...",
    "structured_text": "...",
    "cleaned_text": "Texto limpo e formatado"
}
```

**Exemplo:**
```python
client = ExtractorClient()
result = client.extract_text("documento.pdf")

if result['success']:
    print(result['cleaned_text'])
else:
    print("Erro:", result['error'])
```

---

#### 🐛 **`extract_text_debug(file_path)`** - Extrair com debug

```python
def extract_text_debug(self, file_path: str) -> dict:
    # ... igual ao extract_text mas usa endpoint /extract-debug
```

**O que faz:**
- Igual a `extract_text()` mas retorna **informações adicionais**

**Retorno extra:**
```python
{
    "file_size": 1024000,           # bytes
    "raw_text_length": 5432,        # caracteres
    "structured_text_length": 5876
}
```

---

### 2️⃣ **Função `main()`** (linhas 100-189)

É a **interface de linha de comando** do cliente. Permite usar o script diretamente do terminal.

#### 📝 **Argumentos suportados:**

```bash
python client.py <command> [options]
```

**Comandos:**
- `health` - Verificar saúde da API
- `formats` - Listar formatos
- `extract` - Extrair texto

**Opções:**
- `--file <caminho>` - Caminho do arquivo (obrigatório para `extract`)
- `--url <url>` - URL da API (padrão: `http://localhost:8000`)
- `--debug` - Ativa modo debug
- `--output <arquivo>` - Salva resultado em arquivo JSON

---

## 💡 Exemplos Práticos

### ✅ 1. Verificar saúde da API

```bash
python client.py health
```

**Output:**
```
Verificando saúde da API...
{
  "status": "ok",
  "supported_formats": [
    ".jpeg",
    ".jpg",
    ".pdf",
    ".png",
    ".xlsx",
    ".xlsm"
  ]
}
```

---

### ✅ 2. Listar formatos suportados

```bash
python client.py formats
```

**Output:**
```
Formatos suportados:
  .jpeg
  .jpg
  .pdf
  .png
  .xlsx
  .xlsm
```

---

### ✅ 3. Extrair texto de PDF

```bash
python client.py extract --file documento.pdf
```

**Output:**
```
Extraindo texto de: documento.pdf

================================================================================
Arquivo: documento.pdf
Extensão: .pdf
================================================================================

TEXTO EXTRAÍDO (limpo):

Empresa X
Nota Fiscal Número 001

Data: 01/01/2024
Valor: R$ 1.000,00
...
```

---

### ✅ 4. Extrair com debug

```bash
python client.py extract --file documento.pdf --debug
```

**Output extra:**
```
Tamanho: 1024000 bytes
Texto bruto: 5432 caracteres
Texto estruturado: 5876 caracteres
```

---

### ✅ 5. Salvar resultado em arquivo

```bash
python client.py extract --file documento.pdf --output resultado.json
```

**Cria `resultado.json` com:**
```json
{
  "success": true,
  "filename": "documento.pdf",
  "file_extension": ".pdf",
  "raw_text": "...",
  "structured_text": "...",
  "cleaned_text": "..."
}
```

---

### ✅ 6. Usar com servidor remoto

```bash
python client.py extract --file documento.pdf --url http://seu-servidor.com:8000
```

---

## 📊 Diagrama de Fluxo

```
┌─────────────────────────────┐
│   Terminal (você)           │
│   python client.py ...      │
└──────────────┬──────────────┘
               │
        ┌──────▼─────────┐
        │   main()       │ ← Processa argumentos
        │  (CLI)         │
        └──────┬─────────┘
               │
        ┌──────▼────────────────────────┐
        │   ExtractorClient             │
        │                               │
        │ ├─ health_check()             │
        │ ├─ get_supported_formats()    │
        │ ├─ extract_text()             │
        │ └─ extract_text_debug()       │
        └──────┬────────────────────────┘
               │
        ┌──────▼─────────────────────┐
        │   Requisições HTTP          │
        │   (requests.Session)        │
        │                             │
        │ GET  /health                │
        │ GET  /formats               │
        │ POST /extract (arquivo)     │
        │ POST /extract-debug         │
        └──────┬─────────────────────┘
               │
        ┌──────▼──────────────────────┐
        │   API FastAPI (api.py)      │
        │   em localhost:8000         │
        └─────────────────────────────┘
```

---

## 🎯 Quando usar?

**Use `client.py` para:**

✅ Testar a API do terminal
✅ Integrar em scripts Python
✅ Automatizar extração em lote
✅ Chamar a API de outro programa
✅ Debug e troubleshooting

**Use a API diretamente para:**

- Integração em web apps (JavaScript, React)
- Mobile apps
- Ferramentas externas

---

## 🔗 Relacionado

- **`api.py`** - A API que o cliente consome
- **`processor.py`** - Lógica de extração
- **`main.py`** - CLI alternativa (não usa HTTP)

---

## 🚀 Resumo

**`client.py` é um "controle remoto" da API!** 🎮

Ele permite que você:
- Use a API através de linha de comando
- Integre em scripts e automações Python
- Faça testes rápidos sem precisar de ferramentas externas
- Processe múltiplos arquivos em lote

---

## 📚 Próximas Leituras

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Documentação completa da API
- [EXAMPLE_USAGE.md](EXAMPLE_USAGE.md) - Mais exemplos de uso
- [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) - Detalhes técnicos
