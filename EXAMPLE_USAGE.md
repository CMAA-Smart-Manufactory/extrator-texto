# Exemplos de Uso da API

Guia prático com exemplos de como integrar e usar a API de extração de texto.

## Índice

1. [Setup Inicial](#setup-inicial)
2. [Cliente Python](#cliente-python)
3. [Cliente cURL](#cliente-curl)
4. [Cliente JavaScript](#cliente-javascript)
5. [Cliente Node.js](#cliente-nodejs)
6. [Integração em Web App](#integração-em-web-app)
7. [Casos de Uso](#casos-de-uso)

---

## Setup Inicial

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Iniciar o servidor API

```bash
# Modo desenvolvimento
python api.py

# Ou com Uvicorn direto
python -m uvicorn api:app --reload
```

### 3. Verificar status

```bash
curl http://localhost:8000/health
# Resposta:
# {"status":"ok","supported_formats":[".pdf",".jpg",".png",".jpeg",".xlsx",".xlsm"]}
```

---

## Cliente Python

### Uso com cliente.py

```bash
# Verificar saúde
python client.py health

# Listar formatos
python client.py formats

# Extrair de um arquivo
python client.py extract --file documento.pdf

# Modo debug
python client.py extract --file documento.pdf --debug

# Salvar resultado em JSON
python client.py extract --file documento.pdf --output resultado.json
```

### Importar como módulo

```python
from client import ExtractorClient

# Criar cliente
client = ExtractorClient("http://localhost:8000")

# Verificar saúde
health = client.health_check()
print(f"Status: {health['status']}")
print(f"Formatos: {health['supported_formats']}")

# Extrair texto
result = client.extract_text("documento.pdf")

if result['success']:
    print("Texto extraído com sucesso!")
    print(result['cleaned_text'])
else:
    print(f"Erro: {result['error']}")
```

### Usar requests diretamente

```python
import requests
import json

# Fazer requisição
with open('documento.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/extract', files=files)

# Processar resposta
if response.status_code == 200:
    result = response.json()
    print(result['cleaned_text'])
    
    # Salvar textos em arquivo
    with open('resultado.txt', 'w', encoding='utf-8') as f:
        f.write(f"=== TEXTO BRUTO ===\n{result['raw_text']}\n\n")
        f.write(f"=== TEXTO ESTRUTURADO ===\n{result['structured_text']}\n\n")
        f.write(f"=== TEXTO LIMPO ===\n{result['cleaned_text']}")
else:
    print(f"Erro: {response.json()}")
```

### Processar múltiplos arquivos

```python
import requests
from pathlib import Path

def process_directory(directory_path, output_dir):
    """Processa todos os arquivos suportados em um diretório."""
    
    Path(output_dir).mkdir(exist_ok=True)
    
    for file_path in Path(directory_path).glob('*'):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in ['.pdf', '.jpg', '.png', '.jpeg', '.xlsx', '.xlsm']:
                print(f"Processando {file_path.name}...")
                
                try:
                    with open(file_path, 'rb') as f:
                        files = {'file': f}
                        response = requests.post(
                            'http://localhost:8000/extract',
                            files=files,
                            timeout=60
                        )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Salvar resultado
                        output_file = Path(output_dir) / f"{file_path.stem}.txt"
                        with open(output_file, 'w', encoding='utf-8') as out:
                            out.write(result['cleaned_text'])
                        
                        print(f"  ✓ Salvo em {output_file}")
                    else:
                        print(f"  ✗ Erro: {response.json()['detail']}")
                
                except Exception as e:
                    print(f"  ✗ Erro: {e}")

# Usar
process_directory('arquivos/', 'resultados/')
```

---

## Cliente cURL

### Extração básica

```bash
# Extrair de PDF
curl -X POST http://localhost:8000/extract \
  -F "file=@documento.pdf"

# Extrair de imagem
curl -X POST http://localhost:8000/extract \
  -F "file=@recibo.jpg"

# Extrair de planilha
curl -X POST http://localhost:8000/extract \
  -F "file=@dados.xlsx"
```

### Salvar resposta

```bash
# Salvar JSON completo
curl -X POST http://localhost:8000/extract \
  -F "file=@documento.pdf" \
  | python -m json.tool > resultado.json

# Salvar apenas texto limpo
curl -X POST http://localhost:8000/extract \
  -F "file=@documento.pdf" \
  | python -c "import sys, json; \
    data = json.load(sys.stdin); \
    print(data['cleaned_text'])" > texto.txt
```

### Shell script para múltiplos arquivos

```bash
#!/bin/bash
# script.sh

API_URL="http://localhost:8000"
INPUT_DIR="arquivos"
OUTPUT_DIR="resultados"

mkdir -p "$OUTPUT_DIR"

for file in "$INPUT_DIR"/*{.pdf,.jpg,.png,.jpeg,.xlsx,.xlsm}; do
    [ -e "$file" ] || continue
    
    filename=$(basename "$file")
    echo "Processando: $filename"
    
    response=$(curl -s -X POST "$API_URL/extract" \
      -F "file=@$file")
    
    # Extrair texto limpo e salvar
    cleaned=$(echo "$response" | python -c "import sys, json; \
      data = json.load(sys.stdin); \
      print(data.get('cleaned_text', ''))" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$cleaned" ]; then
        echo "$cleaned" > "$OUTPUT_DIR/${filename%.*}.txt"
        echo "  ✓ Salvo"
    else
        echo "  ✗ Erro ao processar"
    fi
done
```

```bash
chmod +x script.sh
./script.sh
```

---

## Cliente JavaScript

### Fetch API

```javascript
// Extração simples
async function extractText(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:8000/extract', {
    method: 'POST',
    body: formData
  });

  if (response.ok) {
    const result = await response.json();
    console.log('Texto extraído:');
    console.log(result.cleaned_text);
    return result;
  } else {
    const error = await response.json();
    console.error('Erro:', error.detail);
    throw error;
  }
}

// Uso
const fileInput = document.querySelector('input[type="file"]');
fileInput.addEventListener('change', async (e) => {
  try {
    const result = await extractText(e.target.files[0]);
    document.querySelector('#result').textContent = result.cleaned_text;
  } catch (error) {
    alert('Erro: ' + error);
  }
});
```

### React Hook

```jsx
import React, { useState } from 'react';

function ExtractorComponent() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileUpload = async (file) => {
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/extract', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Erro ao processar arquivo');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,.xlsx,.xlsm"
        onChange={(e) => handleFileUpload(e.target.files[0])}
        disabled={loading}
      />

      {loading && <p>Processando...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {result && (
        <div>
          <h3>Arquivo: {result.filename}</h3>
          <pre>{result.cleaned_text}</pre>
        </div>
      )}
    </div>
  );
}

export default ExtractorComponent;
```

### Vue 3 Component

```vue
<template>
  <div class="extractor">
    <input
      type="file"
      accept=".pdf,.png,.jpg,.jpeg,.xlsx,.xlsm"
      @change="handleFileUpload"
      :disabled="loading"
    />

    <div v-if="loading" class="loading">Processando...</div>
    <div v-if="error" class="error">{{ error }}</div>
    
    <div v-if="result" class="result">
      <h3>{{ result.filename }}</h3>
      <p><strong>Tipo:</strong> {{ result.file_extension }}</p>
      <pre>{{ result.cleaned_text }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const result = ref(null);
const loading = ref(false);
const error = ref(null);

const handleFileUpload = async (event) => {
  const file = event.target.files?.[0];
  if (!file) return;

  loading.value = true;
  error.value = null;

  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/extract', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error('Erro ao processar arquivo');
    }

    result.value = await response.json();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.loading { color: blue; }
.error { color: red; }
.result pre { 
  background: #f5f5f5; 
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
```

---

## Cliente Node.js

### Usando axios

```javascript
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

async function extractText(filePath) {
  try {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));

    const response = await axios.post(
      'http://localhost:8000/extract',
      form,
      { headers: form.getHeaders() }
    );

    return response.data;
  } catch (error) {
    console.error('Erro:', error.response?.data || error.message);
    throw error;
  }
}

// Usar
extractText('documento.pdf')
  .then(result => {
    console.log('Texto extraído:');
    console.log(result.cleaned_text);
    
    // Salvar em arquivo
    fs.writeFileSync('resultado.txt', result.cleaned_text);
  });
```

### Express Middleware

```javascript
const express = require('express');
const multer = require('multer');
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/upload', upload.single('file'), async (req, res) => {
  try {
    const form = new FormData();
    form.append('file', fs.createReadStream(req.file.path));

    const response = await axios.post(
      'http://localhost:8000/extract',
      form,
      { headers: form.getHeaders() }
    );

    // Limpar arquivo temporário
    fs.unlinkSync(req.file.path);

    res.json({
      success: true,
      filename: req.file.originalname,
      text: response.data.cleaned_text
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.listen(3000);
```

---

## Integração em Web App

### HTML + jQuery

```html
<!DOCTYPE html>
<html>
<head>
    <title>Extrator de Texto</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 50px auto;
            padding: 20px;
        }
        .upload-area {
            border: 2px dashed #ccc;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            border-radius: 4px;
        }
        .upload-area.drag-over {
            background-color: #f0f0f0;
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 4px;
        }
        pre {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            max-height: 400px;
        }
        .loading {
            color: blue;
            font-weight: bold;
        }
        .error {
            color: red;
            font-weight: bold;
        }
        .success {
            color: green;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>Extrator de Texto de Documentos</h1>
    
    <div class="upload-area" id="uploadArea">
        <p>Arraste arquivos aqui ou clique para selecionar</p>
        <input type="file" id="fileInput" 
               accept=".pdf,.png,.jpg,.jpeg,.xlsx,.xlsm" 
               style="display:none;">
    </div>

    <div id="result"></div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        const uploadArea = $('#uploadArea');
        const fileInput = $('#fileInput');
        const resultDiv = $('#result');

        // Click to upload
        uploadArea.click(() => fileInput.click());

        // Drag and drop
        uploadArea.on('dragover', (e) => {
            e.preventDefault();
            uploadArea.addClass('drag-over');
        });

        uploadArea.on('dragleave', () => {
            uploadArea.removeClass('drag-over');
        });

        uploadArea.on('drop', (e) => {
            e.preventDefault();
            uploadArea.removeClass('drag-over');
            const files = e.originalEvent.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        // File input change
        fileInput.change((e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        function handleFile(file) {
            const formData = new FormData();
            formData.append('file', file);

            resultDiv.html('<div class="loading">Processando ' + 
                           file.name + '...</div>');

            $.ajax({
                url: '/extract',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: (result) => {
                    resultDiv.html(`
                        <div class="result">
                            <h3>${result.filename}</h3>
                            <p><strong>Tipo:</strong> ${result.file_extension}</p>
                            <div class="success">✓ Processado com sucesso</div>
                            <h4>Texto Extraído:</h4>
                            <pre>${escapeHtml(result.cleaned_text)}</pre>
                        </div>
                    `);
                },
                error: (xhr) => {
                    const error = xhr.responseJSON?.detail || 'Erro desconhecido';
                    resultDiv.html(`
                        <div class="error">✗ Erro: ${error}</div>
                    `);
                }
            });
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
```

---

## Casos de Uso

### 1. Pipeline de Processamento em Lote

```python
from client import ExtractorClient
from pathlib import Path
import json

def batch_process(directory, output_format='json'):
    """Processa todos arquivos em um diretório."""
    
    client = ExtractorClient()
    results = []
    
    for file_path in Path(directory).glob('*'):
        if file_path.suffix.lower() not in ['.pdf', '.jpg', '.png', '.jpeg', '.xlsx', '.xlsm']:
            continue
        
        print(f"Processando {file_path.name}...", end=' ', flush=True)
        
        try:
            result = client.extract_text(str(file_path))
            results.append(result)
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
    
    # Salvar resultados
    if output_format == 'json':
        with open('resultados.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    return results

# Usar
batch_process('arquivos/')
```

### 2. Webhook para Notificação

```python
from fastapi import FastAPI, BackgroundTasks
from client import ExtractorClient
import requests

app = FastAPI()

def process_and_notify(file_path: str, webhook_url: str):
    """Processa arquivo e envia resultado via webhook."""
    
    client = ExtractorClient()
    
    try:
        result = client.extract_text(file_path)
        result['status'] = 'success'
    except Exception as e:
        result = {'status': 'error', 'error': str(e)}
    
    # Enviar para webhook
    requests.post(webhook_url, json=result)

@app.post("/extract-async")
async def extract_async(file_path: str, webhook_url: str, 
                       background_tasks: BackgroundTasks):
    background_tasks.add_task(process_and_notify, file_path, webhook_url)
    return {"message": "Processing started"}
```

### 3. Cache de Resultados

```python
import hashlib
import json
from pathlib import Path

class CachedExtractor:
    def __init__(self, cache_dir='.cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.client = ExtractorClient()
    
    def _get_file_hash(self, file_path):
        """Calcula hash do arquivo."""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def extract(self, file_path):
        """Extrai com cache."""
        file_hash = self._get_file_hash(file_path)
        cache_file = self.cache_dir / f"{file_hash}.json"
        
        # Retornar do cache se existir
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # Processar e cachear
        result = self.client.extract_text(file_path)
        with open(cache_file, 'w') as f:
            json.dump(result, f)
        
        return result

# Usar
cached = CachedExtractor()
result = cached.extract('documento.pdf')  # Processa
result = cached.extract('documento.pdf')  # Do cache (instant)
```

---

Mais exemplos e casos de uso em breve!
