import json
import os

META_FILE = "db_meta.json"
DATA_DIR = "data"


def load_metadata(filepath: str) -> dict:
    """Load metadata from JSON file. If file not found, return empty dict."""
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    """Save metadata dict to JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _table_path(table_name: str) -> str:
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name: str) -> list[dict]:
    """Load table data from data/<table>.json. If not found, return empty list."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = _table_path(table_name)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list[dict]) -> None:
    """Save table data to data/<table>.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = _table_path(table_name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

