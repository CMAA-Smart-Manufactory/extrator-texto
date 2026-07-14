"""Cliente de exemplo para usar a API de extração de texto."""

import requests
import json
import sys
from pathlib import Path


class ExtractorClient:
    """Cliente para interagir com a API de extração de texto."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Inicializa o cliente.

        Args:
            base_url: URL base da API (padrão: http://localhost:8000)
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def health_check(self) -> dict:
        """
        Verifica se a API está funcionando.

        Returns:
            Dicionário com status e formatos suportados
        """
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def get_supported_formats(self) -> list[str]:
        """
        Obtém lista de formatos suportados.

        Returns:
            Lista de extensões suportadas
        """
        response = self.session.get(f"{self.base_url}/formats")
        response.raise_for_status()
        data = response.json()
        return data.get("supported_formats", [])

    def extract_text(self, file_path: str) -> dict:
        """
        Extrai texto de um arquivo.

        Args:
            file_path: Caminho para o arquivo

        Returns:
            Dicionário com textos extraídos

        Raises:
            FileNotFoundError: Se arquivo não existe
            requests.HTTPError: Se erro na requisição
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        with open(file_path_obj, "rb") as f:
            files = {"file": (file_path_obj.name, f)}
            response = self.session.post(f"{self.base_url}/extract", files=files)

        response.raise_for_status()
        return response.json()

    def extract_text_debug(self, file_path: str) -> dict:
        """
        Extrai texto com informações de debug.

        Args:
            file_path: Caminho para o arquivo

        Returns:
            Dicionário com detalhes adicionais

        Raises:
            FileNotFoundError: Se arquivo não existe
            requests.HTTPError: Se erro na requisição
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        with open(file_path_obj, "rb") as f:
            files = {"file": (file_path_obj.name, f)}
            response = self.session.post(
                f"{self.base_url}/extract-debug", files=files
            )

        response.raise_for_status()
        return response.json()


def main():
    """Exemplo de uso do cliente."""
    import argparse

    parser = argparse.ArgumentParser(description="Cliente para API de extração de texto")
    parser.add_argument("command", choices=["health", "formats", "extract"], help="Comando")
    parser.add_argument("--file", help="Caminho do arquivo (obrigatório para 'extract')")
    parser.add_argument("--url", default="http://localhost:8000", help="URL base da API")
    parser.add_argument("--debug", action="store_true", help="Modo debug")
    parser.add_argument("--output", help="Salvar resultado em arquivo")

    args = parser.parse_args()

    client = ExtractorClient(args.url)

    try:
        if args.command == "health":
            print("Verificando saúde da API...")
            result = client.health_check()
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "formats":
            print("Formatos suportados:")
            formats = client.get_supported_formats()
            for fmt in formats:
                print(f"  {fmt}")

        elif args.command == "extract":
            if not args.file:
                print("Erro: --file é obrigatório para 'extract'")
                sys.exit(1)

            print(f"Extraindo texto de: {args.file}")

            if args.debug:
                result = client.extract_text_debug(args.file)
            else:
                result = client.extract_text(args.file)

            # Salvar resultado
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"Resultado salvo em: {args.output}")

            # Exibir resultado
            print("\n" + "=" * 80)
            print(f"Arquivo: {result.get('filename')}")
            print(f"Extensão: {result.get('file_extension')}")
            if args.debug:
                print(f"Tamanho: {result.get('file_size')} bytes")
                print(f"Texto bruto: {result.get('raw_text_length')} caracteres")
                print(f"Texto estruturado: {result.get('structured_text_length')} caracteres")
            print("=" * 80)
            print("\nTEXTO EXTRAÍDO (limpo):\n")
            print(result.get("cleaned_text", ""))

    except FileNotFoundError as e:
        print(f"Erro: {e}")
        sys.exit(1)
    except requests.HTTPError as e:
        print(f"Erro na requisição: {e}")
        if e.response.text:
            print(f"Detalhes: {e.response.text}")
        sys.exit(1)
    except requests.ConnectionError:
        print(f"Erro: Não foi possível conectar a {args.url}")
        print("Verifique se a API está rodando: python api.py")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
