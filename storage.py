import json
import os

DATA_PATH = os.path.join("data", "population.json")

def load_population_data() -> list[dict]: # Загружает данные о населении из JSON-файла
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Файл данных не найден: {DATA_PATH}")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data
