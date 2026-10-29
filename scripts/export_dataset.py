"""CLI Script: Export TestGap dataset to canonical JSONL or partitioned splits."""
import sys
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from testgap.services.export_service import ExportService
from testgap.config import EXPORT_DIR


def main():
    parser = argparse.ArgumentParser(description="Exportador de Datasets TestGap")
    parser.add_argument("--mode", choices=["full", "splits"], default="splits", help="Modo de exportação (full ou splits)")
    parser.add_argument("--out", "-o", default=str(EXPORT_DIR), help="Diretório de saída")
    parser.add_argument("--include-unapproved", action="store_true", help="Incluir registros não aprovados")
    args = parser.parse_args()

    service = ExportService()
    only_approved = not args.include_unapproved

    if args.mode == "splits":
        print(f"[*] Exportando particionamento de treino/val/teste para: {args.out}")
        results = service.export_for_training(output_dir=args.out, only_approved=only_approved)
        for sname, sinfo in results.items():
            print(f"  [+] {sname}.jsonl: {sinfo['count']} registros (Grupos: {', '.join(sinfo['groups'])})")
    else:
        out_file = Path(args.out) / "dataset_full.jsonl"
        print(f"[*] Exportando dataset completo para: {out_file}")
        count, path = service.export_dataset(out_file, only_approved=only_approved)
        print(f"  [+] Exportados {count} registros para {path}")


if __name__ == "__main__":
    main()
