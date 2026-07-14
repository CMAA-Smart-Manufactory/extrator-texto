# Quick Start - Início Rápido

Guia rápido para começar a usar a API em menos de 5 minutos.

## ⚡ Instalação e Início (5 minutos)

### 1. Clonar e preparar

```bash
# Clonar repositório
git clone <URL>
cd leitor_arquivos

# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/macOS)
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Iniciar API

```bash
python api.py
```

✅ **API pronta em http://localhost:8000**

---

## 🧪 Teste Rápido

### Abrir documentação (no navegador)

```
http://localhost:8000/docs
```

### Extrair texto (terminal)

```bash
# Linux/macOS
curl -X POST http://localhost:8000/extract \
  -F "file=@seu_arquivo.pdf"

# Windows (PowerShell)
$form = @{ file = [System.IO.File]::ReadAllBytes('arquivo.pdf') }
Invoke-RestMethod -Uri http://localhost:8000/extract `
  -Method Post -Form $form
```

---

## 🚀 Usar CLI (alternativa à API)

```bash
# Processar um arquivo
python main.py documento.pdf

# Processar pasta inteira
python main.py arquivos/
```

---

## 📊 Usar Cliente Python

```bash
# Verificar saúde da API
python client.py health

# Extrair e salvar resultado
python client.py extract --file documento.pdf --output resultado.json
```

---

## 🐳 Docker (alternativa)

```bash
# Build e run
docker-compose up

# API em http://localhost:8000
```

---

## 📚 Próximos Passos

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Guia completo da API
- [EXAMPLE_USAGE.md](EXAMPLE_USAGE.md) - Exemplos de integração
- [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md) - Detalhes técnicos

---

## ❓ Troubleshooting

### Porta 8000 em uso
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8000
kill -9 <PID>
```

### Erro de módulos
```bash
pip install --upgrade -r requirements.txt
```

### Erro de OCR na primeira execução
Paciência! Modelo português está sendo baixado (~500MB). Próximas execuções serão rápidas.

---

## ✨ Formatos Suportados

- 📄 **PDF** - Extração digital
- 🖼️ **PNG, JPG, JPEG** - OCR com português
- 📊 **XLSX, XLSM** - Planilhas Excel

---

**Pronto? Comece agora!** 🎉
