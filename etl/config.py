import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/bi_platform",
)

EXTERNAL_API_BASE_URL = os.getenv("EXTERNAL_API_BASE_URL", "https://api.example.com")
EXTERNAL_API_KEY = os.getenv("EXTERNAL_API_KEY", "")

CSV_DATA_DIR = os.getenv("CSV_DATA_DIR", os.path.join(os.path.dirname(__file__), "data"))

LOG_DIR = os.getenv("LOG_DIR", os.path.join(os.path.dirname(__file__), "logs"))

BATCH_SIZE = int(os.getenv("ETL_BATCH_SIZE", "1000"))
