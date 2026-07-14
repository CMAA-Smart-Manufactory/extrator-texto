"""Módulo de processamento de extração de texto de arquivos."""

import os
import re
import fitz
import cv2
import easyocr
import openpyxl

SUPPORTED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.xlsx', '.xlsm'}


def extract_text_from_image(file_path: str) -> tuple[str, str]:
    """
    Extrai texto de imagens usando OCR (easyocr).
    
    Args:
        file_path: Caminho para o arquivo de imagem
        
    Returns:
        Tupla (raw_text, structured_text)
        
    Raises:
        ValueError: Se a imagem não puder ser lida
    """
    image = cv2.imread(file_path)
    if image is None:
        raise ValueError(f"Não foi possível ler a imagem: {file_path}")

    reader = easyocr.Reader(['pt'], gpu=False)
    # get detailed results with bounding boxes to try to preserve layout
    results = reader.readtext(image, detail=1, paragraph=False)

    # raw text (simple concatenation)
    raw_lines = [res[1] for res in results]
    raw_text = '\n'.join(raw_lines)

    # reconstruct approximate layout grouping by center-y of bbox
    entries = []
    for bbox, text, _ in results:
        x0 = int(bbox[0][0])
        y0 = int(bbox[0][1])
        x1 = int(bbox[2][0])
        y1 = int(bbox[2][1])
        cy = (y0 + y1) / 2
        entries.append((x0, x1, cy, text))

    # group into rows
    rows: list[list[tuple[int, int, float, str]]] = []
    rows_y: list[float] = []
    for e in sorted(entries, key=lambda r: (r[2], r[0])):
        placed = False
        for idx, ry in enumerate(rows_y):
            if abs(e[2] - ry) <= max(10, ry * 0.01):
                rows[idx].append(e)
                # update average y
                rows_y[idx] = (rows_y[idx] * (len(rows[idx]) - 1) + e[2]) / len(rows[idx])
                placed = True
                break
        if not placed:
            rows.append([e])
            rows_y.append(e[2])

    structured_lines: list[str] = []
    for row in rows:
        row_sorted = sorted(row, key=lambda r: r[0])
        if not row_sorted:
            continue
        line_parts = []
        prev_x = row_sorted[0][0]
        for x0, x1, _, text in row_sorted:
            gap = max(0, x0 - prev_x)
            spaces = ' ' * (max(1, int(gap / 20)))
            if not line_parts:
                # initial indentation
                indent = ' ' * max(0, int(x0 / 20))
                line_parts.append(indent + text)
            else:
                line_parts.append(spaces + text)
            prev_x = x1
        structured_lines.append(''.join(line_parts))

    structured_text = '\n'.join(structured_lines)
    return raw_text, structured_text


def extract_text_from_pdf(file_path: str) -> tuple[str, str]:
    """
    Extrai texto de arquivos PDF.
    
    Args:
        file_path: Caminho para o arquivo PDF
        
    Returns:
        Tupla (raw_text, structured_text)
    """
    text_parts = []
    structured_parts = []
    with fitz.open(file_path) as doc:
        for page_no, page in enumerate(doc, start=1):
            text = page.get_text("text")
            if text:
                text_parts.append(text)

            # use blocks to preserve approximate layout
            try:
                blocks = page.get_text("blocks")  # list of (x0,y0,x1,y1, text, block_no)
            except Exception:
                blocks = []

            page_lines: list[str] = []
            for b in sorted(blocks, key=lambda b: (b[1], b[0])):
                x0 = int(b[0])
                block_text = str(b[4]).strip()
                if not block_text:
                    continue
                indent = ' ' * max(0, int(x0 / 8))
                for line in block_text.splitlines():
                    page_lines.append(indent + line)

            if page_lines:
                structured_parts.append('\n'.join(page_lines))

    return '\n'.join(text_parts), '\n\n'.join(structured_parts)


def extract_text_from_excel(file_path: str) -> tuple[str, str]:
    """
    Extrai texto de arquivos Excel.
    
    Args:
        file_path: Caminho para o arquivo Excel (.xlsx, .xlsm)
        
    Returns:
        Tupla (raw_text, structured_text)
    """
    workbook = openpyxl.load_workbook(file_path, data_only=True)
    raw_parts = []
    structured_parts = []

    for sheet in workbook.worksheets:
        rows: list[list[str]] = []
        for row in sheet.iter_rows(values_only=True):
            cells = [str(cell).strip() if cell is not None else '' for cell in row]
            if any(cells):
                rows.append(cells)

        # raw text: simple concatenation
        raw_parts.append(f"## Planilha: {sheet.title}")
        for r in rows:
            raw_parts.append(' '.join([c for c in r if c]))

        # structured: align columns
        if rows:
            col_count = max(len(r) for r in rows)
            widths = [0] * col_count
            for r in rows:
                for i in range(col_count):
                    val = r[i] if i < len(r) else ''
                    widths[i] = max(widths[i], len(val))

            structured_parts.append(f"## Planilha: {sheet.title}")
            for r in rows:
                cells = [(r[i] if i < len(r) else '').ljust(widths[i]) for i in range(col_count)]
                structured_parts.append(' | '.join(cells))

    return '\n'.join(raw_parts), '\n'.join(structured_parts)


def extract_text(file_path: str) -> tuple[str, str]:
    """
    Extrai texto de um arquivo com base em seu tipo.
    
    Args:
        file_path: Caminho para o arquivo
        
    Returns:
        Tupla (raw_text, structured_text)
        
    Raises:
        ValueError: Se o formato não for suportado
    """
    _, extension = os.path.splitext(file_path.lower())
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Formato não suportado: {extension}")

    if extension in {'.png', '.jpg', '.jpeg'}:
        return extract_text_from_image(file_path)
    if extension == '.pdf':
        return extract_text_from_pdf(file_path)
    if extension in {'.xlsx', '.xlsm'}:
        return extract_text_from_excel(file_path)

    raise ValueError(f"Formato inválido ou não suportado: {extension}")


def get_supported_files_in_directory(directory_path: str) -> list[str]:
    """
    Encontra todos os arquivos suportados em um diretório.
    
    Args:
        directory_path: Caminho do diretório
        
    Returns:
        Lista de caminhos de arquivos suportados
    """
    files = []
    for entry in sorted(os.listdir(directory_path)):
        full_path = os.path.join(directory_path, entry)
        if os.path.isfile(full_path):
            _, extension = os.path.splitext(entry.lower())
            if extension in SUPPORTED_EXTENSIONS:
                files.append(full_path)
    return files


def clean_text_for_reading(text: str) -> str:
    """
    Simplifica espaços em branco e agrupa linhas curtas para melhor legibilidade.
    
    Args:
        text: Texto a ser limpo
        
    Returns:
        Texto limpo e formatado
    """
    if not text:
        return ""

    # normalize whitespace and split
    lines = [re.sub(r"\s+", " ", l).strip() for l in text.splitlines()]
    lines = [l for l in lines if l]

    merged: list[str] = []
    i = 0
    while i < len(lines):
        cur = lines[i]
        # try to merge with following lines when current line is short
        while i + 1 < len(lines) and len(cur) < 40 and len(lines[i + 1]) < 80:
            cur = cur + ' ' + lines[i + 1]
            i += 1
        merged.append(cur)
        i += 1

    return '\n'.join(merged)


def is_supported_format(file_extension: str) -> bool:
    """
    Verifica se um formato de arquivo é suportado.
    
    Args:
        file_extension: Extensão do arquivo (ex: '.pdf')
        
    Returns:
        True se suportado, False caso contrário
    """
    return file_extension.lower() in SUPPORTED_EXTENSIONS


def get_supported_formats() -> list[str]:
    """
    Retorna lista de formatos suportados.
    
    Returns:
        Lista de extensões suportadas
    """
    return sorted(list(SUPPORTED_EXTENSIONS))
