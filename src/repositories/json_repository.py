# src/repositories/json_repository.py
import os
import json
from src.config.constants import DATA_DIR

class JSONRepository:
    @staticmethod
    def _get_path(filename: str) -> str:
        os.makedirs(DATA_DIR, exist_ok=True)
        return os.path.join(DATA_DIR, filename)

    @staticmethod
    def load_data(filename: str) -> list | dict:
        filepath = JSONRepository._get_path(filename)
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def save_data(filename: str, data) -> bool:
        filepath = JSONRepository._get_path(filename)
        temp_path = filepath + ".tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            os.replace(temp_path, filepath)
            return True
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False