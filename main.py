import argparse
import os

from processor import (
    extract_text,
    get_supported_files_in_directory,
    clean_text_for_reading,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extrai texto bruto e dados de arquivos de notas fiscais e recibos."
    )
    parser.add_argument(
        "path",
        help="Caminho para um arquivo ou uma pasta contendo arquivos suportados (.pdf, .png, .jpg, .jpeg, .xlsx, .xlsm)",
    )
    args = parser.parse_args()

    path = args.path

    if not os.path.exists(path):
        print(f"Erro: caminho não encontrado: {path}")
        return

    target_files = []
    if os.path.isdir(path):
        target_files = get_supported_files_in_directory(path)
        if not target_files:
            print(f"Nenhum arquivo suportado encontrado na pasta: {path}")
            return
    else:
        target_files = [path]

    for index, file_path in enumerate(target_files, start=1):
        print("\n" + "=" * 80)
        print(f"Arquivo {index}/{len(target_files)}: {file_path}")
        print("=" * 80)

        if not os.path.isfile(file_path):
            print(f"Erro: arquivo não encontrado: {file_path}")
            continue

        try:
            raw_text, structured_text = extract_text(file_path)
            # prefer structured text when available
            text_to_use = structured_text if structured_text else raw_text

            # clean text for readable output and print only that
            cleaned = clean_text_for_reading(text_to_use)
            print(cleaned)
        except Exception as exc:
            print(f"Erro ao processar o arquivo: {exc}")


if __name__ == "__main__":
    main()
