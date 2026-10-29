"""CLI Script: Initialize TestGap SQLite database and apply migrations."""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from testgap.database import default_db
from testgap.config import DB_PATH


def main():
    print(f"[*] Inicializando banco de dados SQLite em: {DB_PATH.resolve()}")
    default_db.run_migrations()
    print("[+] Migrações aplicadas com sucesso e categorias padrão semeadas.")


if __name__ == "__main__":
    main()
