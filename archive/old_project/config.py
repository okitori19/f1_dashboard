# config.py
from pathlib import Path

# Корень проекта (папка, где лежит config.py)
BASE_DIR = Path(__file__).resolve().parent

# Папка для сохранения данных
DATA_DIR = BASE_DIR / "csv"

# Автоматически создаем папку ./csv, если ее нет
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Опционально: другие параметры
API_MAX_REQUESTS_PER_MINUTE = 30
API_TIMEOUT = 30