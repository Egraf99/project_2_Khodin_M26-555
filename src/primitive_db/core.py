"""Модуль предназначен для описания основной логики работы с таблицами и данными."""

from typing import List

type Column = tuple[str, str]

def create_table(metadata: dict, table_name: str, columns: List[Column]) -> dict:
    """
    Создает таблицу `table_name`. Автоматически создает колонку ID,
        если не была задана пользователем.

    Args:
        metadata: актуальное состояние базы данных
        table_name: название таблицы
        columns: список колонок в виде пар (<название>, <тип_колонки>),
            допускается в <тип_колонки> только 'int', 'str', 'bool'

    Returns:
        Словарь метаданных с новой таблицей
    """
    exists_tables = metadata.keys()
    if table_name in exists_tables:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    added_columns = [["ID", "int"]]
    for column in columns:
        name, type_ = column

        if type_ not in ("int", "str", "bool"):
            print(
                f'Ошибка: Тип колонки "{name}" неправильный',
                'Допустимые значения: int, str, bool.'
            )
            return metadata

        if name == "ID":
            if type_ != "int":
                print(
                    f'Ошибка: Тип колонки "{name}" неправильный.',
                    'Допустимое значение: int.'
                )
                return metadata
            continue

        added_columns.append([name, type_])

    metadata[table_name] = {"columns": added_columns}
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict:
    """
    Удаляет таблицу из `metadata`, если она там есть, иначе показывает ошибку.
    """
    exists_tables = metadata.keys()
    if table_name not in exists_tables:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    metadata.pop(table_name)
    return metadata


def list_tables(metadata: dict) -> list:
    """
    Возвращает список всех существующих таблиц.
    """
    return list(metadata.keys())
    
