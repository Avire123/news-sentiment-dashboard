import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Database Configuration
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "app_database.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# Ingestion & Execution Settings
SEEDS_FILE = BASE_DIR / "config" / "seeds.json"
HTTP_TIMEOUT = 10
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.5
FETCH_INTERVAL_MINUTES = 15
