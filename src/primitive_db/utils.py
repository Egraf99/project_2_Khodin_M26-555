"""Вспомогательные функции по чтению из файла и записи в файл"""

import json


def load_metadata(filepath: str) -> dict:
    """
    Загрузка файлов из JSON-файла по пути `filepath`. Если файл не найден, возвращается пустой словарь.
    """
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    """
    Сохраняет переданный словарь `data` в файл по пути `filepath`
    """
    with open(filepath, "w") as file:
        json.dump(data, file)


def load_table_data(table_name: str) -> list[dict]:
    """Загружает записи таблицы; если файла нет, возвращает пустой список."""
    try:
        with open(f"data/{table_name}.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list[dict]) -> None:
    """Сохраняет записи таблицы в JSON-файл."""
    with open(f"data/{table_name}.json", "w") as file:
        json.dump(data, file)
