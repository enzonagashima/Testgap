"""CLI Script: Safely backup SQLite database."""
import sys
import shutil
from pathlib import Path
from datetime import datetime, timezone

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from testgap.config import DB_PATH, BACKUP_DIR


def main():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        print(f"[!] Banco de dados não encontrado em {DB_PATH}")
        sys.exit(1)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest_file = BACKUP_DIR / f"testgap_backup_{ts}.db"

    print(f"[*] Criando cópia de segurança de {DB_PATH.name}...")
    shutil.copy2(DB_PATH, dest_file)
    print(f"[+] Backup concluído com sucesso: {dest_file.resolve()}")


if __name__ == "__main__":
    main()
