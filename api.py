"""API FastAPI para extração de texto de arquivos."""

import os
import shutil
import tempfile
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from processor import (
    extract_text,
    clean_text_for_reading,
    is_supported_format,
    get_supported_formats,
)

# --- Configuração via variáveis de ambiente ---
# ALLOWED_ORIGINS: lista separada por vírgula (ex: "https://app.com,https://x.com")
# ou "*" para liberar geral (sem cookies/credentials, por segurança).
_allowed_origins_raw = os.environ.get("ALLOWED_ORIGINS", "*").strip()
ALLOWED_ORIGINS = (
    ["*"] if _allowed_origins_raw == "*"
    else [o.strip() for o in _allowed_origins_raw.split(",") if o.strip()]
)
# Nunca combinar wildcard de origem com credentials=True (é inseguro e
# rejeitado por navegadores modernos).
ALLOW_CREDENTIALS = ALLOWED_ORIGINS != ["*"]

# Se definida, exige o header "X-API-Key" em todas as chamadas.
API_KEY = os.environ.get("API_KEY", "").strip()

# Tamanho máximo de upload em bytes (padrão 50MB).
MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", str(50 * 1024 * 1024)))

# O endpoint /extract-debug expõe texto bruto completo e tamanhos de arquivo;
# mantenha desligado em produção a menos que explicitamente habilitado.
ENABLE_DEBUG_ENDPOINT = os.environ.get("ENABLE_DEBUG_ENDPOINT", "false").strip().lower() in ("1", "true", "yes")


async def verify_api_key(x_api_key: Optional[str] = Header(default=None)):
    """Valida o header X-API-Key quando a variável API_KEY estiver configurada."""
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key inválida ou ausente")
    return True


# Inicializa aplicação FastAPI
app = FastAPI(
    title="Leitor de Arquivos API",
    description="API para extração de texto de arquivos (PDF, imagens, planilhas)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Modelos de resposta
class TextExtractionResponse(BaseModel):
    """Modelo de resposta para extração de texto."""
    success: bool
    filename: str
    file_extension: str
    raw_text: str
    structured_text: str
    cleaned_text: str
    message: str


class ErrorResponse(BaseModel):
    """Modelo de resposta para erros."""
    success: bool
    error: str
    message: str


class HealthResponse(BaseModel):
    """Modelo de resposta de saúde da API."""
    status: str
    supported_formats: list[str]


# Rotas


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Verifica a saúde da API.
    
    Returns:
        Status da API e formatos suportados
    """
    return {
        "status": "ok",
        "supported_formats": get_supported_formats(),
    }


@app.get("/formats")
async def get_formats():
    """
    Retorna lista de formatos de arquivo suportados.
    
    Returns:
        Lista de extensões suportadas
    """
    return {
        "supported_formats": get_supported_formats(),
        "description": "Formatos de arquivo que podem ser processados",
    }


@app.post("/extract", response_model=TextExtractionResponse)
async def extract_file(file: UploadFile = File(...), _auth: bool = Depends(verify_api_key)):
    """
    Extrai texto de um arquivo enviado.
    
    O arquivo é processado para extrair:
    - Texto bruto: concatenação simples do texto encontrado
    - Texto estruturado: preservando layout/estrutura
    - Texto limpo: versão otimizada para leitura
    
    Args:
        file: Arquivo a processar (PDF, PNG, JPG, JPEG, XLSX, XLSM)
        
    Returns:
        TextExtractionResponse com os textos extraídos
        
    Raises:
        HTTPException: Se o formato não for suportado ou houver erro no processamento
    """
    # Validar nome do arquivo
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Nome de arquivo inválido",
        )

    # Obter extensão do arquivo
    _, file_extension = os.path.splitext(file.filename)

    # Validar formato
    if not is_supported_format(file_extension):
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{file_extension}' não suportado. Formatos suportados: {get_supported_formats()}",
        )

    # Criar arquivo temporário
    temp_file_path = None
    try:
        # Salvar arquivo temporário
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension,
            prefix="upload_",
        ) as temp_file:
            temp_file_path = temp_file.name
            total_written = 0
            while chunk := await file.read(1024 * 1024):
                total_written += len(chunk)
                if total_written > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Arquivo excede o tamanho máximo permitido ({MAX_FILE_SIZE} bytes)",
                    )
                temp_file.write(chunk)

        # Processar arquivo
        raw_text, structured_text = extract_text(temp_file_path)

        # Limpar texto para melhor legibilidade
        cleaned_text = clean_text_for_reading(
            structured_text if structured_text else raw_text
        )

        return {
            "success": True,
            "filename": file.filename,
            "file_extension": file_extension,
            "raw_text": raw_text,
            "structured_text": structured_text,
            "cleaned_text": cleaned_text,
            "message": "Arquivo processado com sucesso",
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao processar arquivo: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar arquivo: {str(e)}",
        )
    finally:
        # Limpar arquivo temporário
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass


@app.get("/")
async def root():
    """
    Endpoint raiz com informações da API.
    
    Returns:
        Informações sobre a API e links úteis
    """
    return {
        "name": "Leitor de Arquivos API",
        "version": "1.0.0",
        "description": "API para extração de texto de documentos",
        "endpoints": {
            "health": "/health",
            "formats": "/formats",
            "extract": "/extract",
            "docs": "/docs",
            "redoc": "/redoc",
        },
        "supported_formats": get_supported_formats(),
    }


@app.post("/extract-debug")
async def extract_file_debug(file: UploadFile = File(...), _auth: bool = Depends(verify_api_key)):
    """
    Endpoint de debug para extração com mais detalhes.

    Desabilitado por padrão (ENABLE_DEBUG_ENDPOINT=false) pois expõe texto
    bruto completo e metadados do arquivo. Habilite apenas em ambientes
    controlados.
    
    Args:
        file: Arquivo a processar
        
    Returns:
        Resposta detalhada em JSON
    """
    if not ENABLE_DEBUG_ENDPOINT:
        raise HTTPException(status_code=404, detail="Endpoint não encontrado")

    # Validar nome do arquivo
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Nome de arquivo inválido",
        )

    # Obter extensão do arquivo
    _, file_extension = os.path.splitext(file.filename)

    # Validar formato
    if not is_supported_format(file_extension):
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{file_extension}' não suportado",
        )

    # Criar arquivo temporário
    temp_file_path = None
    try:
        # Salvar arquivo temporário
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension,
            prefix="upload_",
        ) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        # Processar arquivo
        raw_text, structured_text = extract_text(temp_file_path)

        return {
            "success": True,
            "filename": file.filename,
            "file_extension": file_extension,
            "file_size": os.path.getsize(temp_file_path),
            "raw_text_length": len(raw_text),
            "structured_text_length": len(structured_text),
            "raw_text": raw_text,
            "structured_text": structured_text,
            "cleaned_text": clean_text_for_reading(
                structured_text if structured_text else raw_text
            ),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
    finally:
        # Limpar arquivo temporário
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
    )
