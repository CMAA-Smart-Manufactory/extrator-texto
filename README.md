# Leitor de Notas Fiscais e Recibos

Projeto Python para extrair textos brutos de arquivos de notas fiscais, recibos e planilhas **via CLI ou API REST**.

## Recursos Principais

- ✅ **API FastAPI** - Interface HTTP para extração de texto
- ✅ **CLI** - Interface de linha de comando para uso local
- ✅ **Múltiplos formatos** - PDF, imagens com OCR, planilhas Excel
- ✅ **Processamento local** - Sem dependência de APIs externas
- ✅ **Documentação automática** - Swagger UI integrado

## Formatos Suportados

| Formato | Tipo | Processamento |
|---------|------|---------------|
| `.pdf` | Documento | PyMuPDF - Extração de texto digital |
| `.png` | Imagem | easyocr + OpenCV - OCR português |
| `.jpg` / `.jpeg` | Imagem | easyocr + OpenCV - OCR português |
| `.xlsx` / `.xlsm` | Planilha | openpyxl - Leitura de células |

## Inicialização Rápida

### 1. Instalação

```bash
# Clonar repositório
git clone <URL_DO_REPOSITORIO>
cd leitor_notas

# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate
# Ativar (Linux/macOS)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Usar via CLI

```bash
python main.py caminho/do/arquivo.pdf
python main.py arquivos/  # processa pasta inteira
```

### 3. Usar via API

```bash
python api.py
```

API disponível em: **http://localhost:8000**
- Documentação interativa: **http://localhost:8000/docs**

## Uso

### Linha de Comando (CLI)

```bash
python main.py <arquivo_ou_pasta>
```

**Exemplos:**

```bash
# Processar um PDF
python main.py documento.pdf

# Processar uma imagem
python main.py recibo.jpg

# Processar pasta inteira
python main.py arquivos
```

**Output:** Texto extraído é exibido no console

### API REST

#### Extrair texto via HTTP

```bash
curl -X POST http://localhost:8000/extract \
  -F "file=@documento.pdf"
```

**Resposta:**

```json
{
  "success": true,
  "filename": "documento.pdf",
  "file_extension": ".pdf",
  "raw_text": "...",
  "structured_text": "...",
  "cleaned_text": "...",
  "message": "Arquivo processado com sucesso"
}
```

#### Verificar saúde da API

```bash
curl http://localhost:8000/health
```

#### Ver formatos suportados

```bash
curl http://localhost:8000/formats
```

Para exemplos completos, veja [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## Estrutura do Projeto

```
leitor_notas/
├── main.py                      # Interface CLI
├── api.py                       # API FastAPI
├── processor.py                 # Núcleo de processamento
├── requirements.txt             # Dependências
├── README.md                    # Este arquivo
├── API_DOCUMENTATION.md         # Documentação detalhada da API
├── TECHNICAL_DOCUMENTATION.md   # Documentação técnica interna
└── arquivos/                    # Pasta com arquivos para processar
```

## Arquitetura

```
CLI (main.py)
    ↓
API (api.py)
    ↓
processor.py (Núcleo)
    ├── extract_text()
    ├── extract_text_from_pdf()
    ├── extract_text_from_image()
    ├── extract_text_from_excel()
    └── clean_text_for_reading()
```

## Dependências

| Pacote | Versão | Propósito |
|--------|--------|----------|
| easyocr | latest | OCR multilíngue |
| pymupdf | latest | Extração de PDF |
| opencv-python-headless | latest | Processamento de imagens |
| openpyxl | latest | Leitura de Excel |
| fastapi | 0.104.1 | Framework web |
| uvicorn | 0.24.0 | Servidor ASGI |
| python-multipart | 0.0.6 | Upload de arquivos |

## Requisitos

- Python 3.9 ou superior
- Conexão com internet (apenas para instalar dependências)
- ~2GB de espaço em disco (para modelos de OCR)

## Tipos de Saída

Cada arquivo processado gera 3 versões de texto:

### 1. Texto Bruto (`raw_text`)
Concatenação simples do texto encontrado:
```
Empresa X
Nota Fiscal
Data: 01/01/2024
Valor: R$ 1.000,00
```

### 2. Texto Estruturado (`structured_text`)
Preserva layout e estrutura:
```
        Empresa X
    Nota Fiscal de Serviço

Data:              01/01/2024
Valor:             R$ 1.000,00
```

### 3. Texto Limpo (`cleaned_text`)
Otimizado para leitura com linhas agrupadas:
```
Empresa X Nota Fiscal de Serviço
Data: 01/01/2024 Valor: R$ 1.000,00
```

## Exemplos de Uso

### Python

```python
# CLI
import subprocess
result = subprocess.run(['python', 'main.py', 'documento.pdf'])

# Ou importar processor diretamente
from processor import extract_text, clean_text_for_reading

raw, structured = extract_text('documento.pdf')
cleaned = clean_text_for_reading(structured or raw)
print(cleaned)
```

### JavaScript/Node

```javascript
import FormData from 'form-data';
import fs from 'fs';
import axios from 'axios';

async function extract() {
  const form = new FormData();
  form.append('file', fs.createReadStream('documento.pdf'));
  
  const response = await axios.post(
    'http://localhost:8000/extract',
    form,
    { headers: form.getHeaders() }
  );
  
  console.log(response.data.cleaned_text);
}

extract();
```

### React

```jsx
import React, { useState } from 'react';

function FileUpload() {
  const [result, setResult] = useState(null);

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/extract', {
      method: 'POST',
      body: formData
    });
    
    setResult(await response.json());
  };

  return (
    <div>
      <input 
        type="file" 
        onChange={(e) => handleUpload(e.target.files[0])}
      />
      {result && <pre>{result.cleaned_text}</pre>}
    </div>
  );
}
```

## Configuração de Produção

### Iniciar em produção

```bash
# Modo daemon com nohup
nohup python -m uvicorn api:app --host 0.0.0.0 --port 8000 &

# Ou com supervisor
pip install supervisor
# Editar supervisord.conf e iniciar
supervisord
```

### Com Docker

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0"]
```

```bash
docker build -t leitor-api .
docker run -p 8000:8000 leitor-api
```

## Resolução de Problemas

### Erro: "Módulo não encontrado"

```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt
```

### Erro: "Não foi possível ler a imagem"

- Verificar se arquivo está corrompido
- Tentar converter para PNG
- Verificar permissões de leitura

### API não inicia na porta 8000

```bash
# Usar porta diferente
python -m uvicorn api:app --port 8001

# Liberar porta 8000
# Windows: netstat -ano | findstr :8000 → taskkill /PID <PID>
# Linux:   lsof -i :8000 → kill -9 <PID>
```

### OCR lento na primeira execução

- Modelo é baixado apenas na primeira vez
- Paciência: OCR português ~500MB
- Próximas execuções serão rápidas

## Melhorias Futuras

- [ ] Suporte para formatos adicionais (DOCX, RTF)
- [ ] Extração de dados estruturados (entidades nomeadas)
- [ ] Cache de resultados
- [ ] Interface web completa
- [ ] Fila de processamento para múltiplos arquivos
- [ ] Autenticação e rate limiting
- [ ] Histórico de processamentos

## Desempenho

| Operação | Tempo Típico |
|----------|-------------|
| PDF simples | 1-2s |
| Imagem com OCR | 5-10s |
| Planilha Excel | 500ms-2s |
| Inicialização (primeira vez) | 30-60s |

## Observações

- Código não utiliza APIs de IA externas
- Processamento 100% local (offline após instalação)
- Requer internet apenas na primeira execução (download de modelos)

## Documentação Adicional

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Guia completo da API
- [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) - Detalhes técnicos internos
- [CLIENT_EXPLICACAO.md](CLIENT_EXPLICACAO.md) - Detalhes de utilização

## Licença

[Sua licença aqui]

## Suporte

[Suas informações de contato]
- Se o arquivo não existir ou o formato não for suportado, uma mensagem de erro amigável será exibida.
