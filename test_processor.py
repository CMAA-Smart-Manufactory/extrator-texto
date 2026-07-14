"""Testes básicos para o módulo processor e API."""

import pytest
import os
from pathlib import Path

from processor import (
    extract_text,
    is_supported_format,
    get_supported_formats,
    clean_text_for_reading,
)


class TestProcessor:
    """Testes do módulo processor."""

    def test_supported_formats(self):
        """Testa obtenção de formatos suportados."""
        formats = get_supported_formats()
        assert isinstance(formats, list)
        assert len(formats) > 0
        assert '.pdf' in formats
        assert '.jpg' in formats
        assert '.xlsx' in formats

    def test_is_supported_format_valid(self):
        """Testa validação de formatos suportados."""
        assert is_supported_format('.pdf') is True
        assert is_supported_format('.jpg') is True
        assert is_supported_format('.jpeg') is True
        assert is_supported_format('.png') is True
        assert is_supported_format('.xlsx') is True
        assert is_supported_format('.xlsm') is True

    def test_is_supported_format_invalid(self):
        """Testa rejeição de formatos não suportados."""
        assert is_supported_format('.doc') is False
        assert is_supported_format('.docx') is False
        assert is_supported_format('.txt') is False
        assert is_supported_format('.ppt') is False

    def test_is_supported_format_case_insensitive(self):
        """Testa case-insensitive para extensões."""
        assert is_supported_format('.PDF') is True
        assert is_supported_format('.JPG') is True
        assert is_supported_format('.Pdf') is True

    def test_clean_text_for_reading_empty_string(self):
        """Testa limpeza de string vazia."""
        result = clean_text_for_reading("")
        assert result == ""

    def test_clean_text_for_reading_single_line(self):
        """Testa limpeza de linha única."""
        text = "  Teste  com  espaços  "
        result = clean_text_for_reading(text)
        assert result == "Teste com espaços"

    def test_clean_text_for_reading_multiple_spaces(self):
        """Testa normalização de múltiplos espaços."""
        text = "Linha    com    múltiplos    espaços"
        result = clean_text_for_reading(text)
        assert result == "Linha com múltiplos espaços"

    def test_clean_text_for_reading_empty_lines(self):
        """Testa remoção de linhas vazias."""
        text = "Linha 1\n\n\nLinha 2\n\nLinha 3"
        result = clean_text_for_reading(text)
        lines = result.split('\n')
        assert "" not in lines

    def test_clean_text_for_reading_short_lines_merge(self):
        """Testa agrupamento de linhas curtas."""
        text = "Muito curta\nLinha que é um pouco maior de acordo com o algoritmo"
        result = clean_text_for_reading(text)
        # Linhas curtas devem ser agrupadas
        lines = result.split('\n')
        assert len(lines) == 1  # Agrupadas em uma linha

    def test_extract_text_unsupported_format(self):
        """Testa erro com formato não suportado."""
        with pytest.raises(ValueError, match="Formato não suportado"):
            extract_text("arquivo.doc")

    def test_extract_text_nonexistent_file(self):
        """Testa erro com arquivo inexistente."""
        with pytest.raises((FileNotFoundError, ValueError)):
            extract_text("arquivo_inexistente.pdf")


class TestTextProcessing:
    """Testes de processamento de texto."""

    def test_clean_text_preserves_content(self):
        """Testa que limpeza preserva conteúdo importante."""
        text = "Empresa X\nData: 01/01/2024\nValor: 1000"
        result = clean_text_for_reading(text)
        assert "Empresa" in result
        assert "Data" in result
        assert "2024" in result
        assert "1000" in result

    def test_clean_text_removes_excessive_newlines(self):
        """Testa remoção de quebras de linha excessivas."""
        text = "\n\n\nTexto\n\n\n"
        result = clean_text_for_reading(text)
        assert result.startswith("Texto")
        assert result.endswith("Texto")

    def test_clean_text_normalizes_whitespace(self):
        """Testa normalização de espaços em branco."""
        text = "Teste\twith\ttabs\nand   spaces"
        result = clean_text_for_reading(text)
        assert "\t" not in result
        assert "   " not in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
