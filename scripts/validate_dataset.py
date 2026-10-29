"""CLI Script: Validate exported JSONL dataset against dataset-v1.schema.json."""
import sys
import json
import argparse
from pathlib import Path
import jsonschema

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from testgap.config import SCHEMAS_DIR


def validate_file(file_path: Path | str) -> bool:
    schema_path = SCHEMAS_DIR / "dataset-v1.schema.json"
    if not schema_path.exists():
        print(f"[!] Erro: Arquivo de schema não encontrado em {schema_path}")
        return False

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    target_file = Path(file_path)
    if not target_file.exists():
        print(f"[!] Erro: Arquivo de dataset não encontrado em {target_file}")
        return False

    total_lines = 0
    errors = 0

    print(f"[*] Validando arquivo '{target_file.name}' contra JSON Schema v1.0.0...")

    with open(target_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line_str = line.strip()
            if not line_str:
                continue
            total_lines += 1
            try:
                record = json.loads(line_str)
                jsonschema.validate(instance=record, schema=schema)
            except json.JSONDecodeError as je:
                print(f"[!] Linha {line_num}: JSON inválido: {je}")
                errors += 1
            except jsonschema.ValidationError as ve:
                print(f"[!] Linha {line_num}: Violação de esquema: {ve.message}")
                errors += 1

    if errors == 0:
        print(f"[+] Sucesso! Todas as {total_lines} linhas obedecem estritamente ao schema.")
        return True
    else:
        print(f"[!] Falha: Foram encontrados {errors} erros em {total_lines} linhas analisadas.")
        return False


def main():
    parser = argparse.ArgumentParser(description="Validador de JSONL para TestGap")
    parser.add_argument("--file", "-f", required=True, help="Caminho do arquivo JSONL a validar")
    args = parser.parse_args()

    success = validate_file(args.file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
