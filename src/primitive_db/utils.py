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


def generate_id(exists_ids: list[int]) -> int:
    """
    Генерирует уникальный ключ ID. Ключ не совпадает ни с одной строкой из `exists_ids`
    """
    existing_ids = set(exists_ids)

    for number in range(1, 10000000):
        if number not in existing_ids:
            return number

    raise ValueError("Все идентификаторы до 7 цифр заняты.")
