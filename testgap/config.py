"""Application configuration and environment settings."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Database configuration
DEFAULT_DB_PATH = BASE_DIR / "data" / "testgap.db"
DB_PATH = Path(os.getenv("TESTGAP_DB_PATH", str(DEFAULT_DB_PATH)))

# Ensure parent directory of DB exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Export and backup directories
EXPORT_DIR = Path(os.getenv("TESTGAP_EXPORT_DIR", str(BASE_DIR / "data" / "exports")))
BACKUP_DIR = Path(os.getenv("TESTGAP_BACKUP_DIR", str(BASE_DIR / "data" / "backups")))
SCHEMAS_DIR = BASE_DIR / "schemas"

EXPORT_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# Pagination and UI settings
DEFAULT_PAGE_SIZE = int(os.getenv("TESTGAP_PAGE_SIZE", "20"))
SCHEMA_VERSION = "1.0.0"
LOG_LEVEL = os.getenv("TESTGAP_LOG_LEVEL", "INFO")
