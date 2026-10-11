"""Модуль предназначен для описания основной логики работы с таблицами и данными."""

from primitive_db.constants import ID_COLUMN, VALID_TYPES
from primitive_db.decorators import confirm_action, handle_db_errors, log_time
from primitive_db.utils import load_table_data

type Column = tuple[str, str]

@handle_db_errors
def create_table(
    metadata: dict, table_name: str, columns: list[Column]
) -> dict | None:
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
        raise ValueError(f'Таблица "{table_name}" уже существует')

    added_columns = [[ID_COLUMN, "int"]]

    for column in columns:
        name, type_ = column

        if type_ not in VALID_TYPES:
            raise ValueError(
                f'Тип колонки "{name}" неправильный. '
                'Допустимые значения: int, str, bool'
            )

        if name == ID_COLUMN:
            if type_ != "int":
                raise ValueError('Столбец "ID" должен иметь тип int')
            continue

        added_columns.append([name, type_])

    metadata[table_name] = {"columns": added_columns}

    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict | None:
    """
    Удаляет таблицу из `metadata`, если она там есть, иначе показывает ошибку.
    """

    table_exists(metadata, table_name)

    metadata.pop(table_name)

    return metadata


def list_tables(metadata: dict) -> list[str]:
    """
    Возвращает список всех существующих таблиц.
    """

    return list(metadata.keys())


def table_exists(metadata: dict, table_name: str) -> bool:
    """Проверяет существование таблицы; при отсутствии вызывает KeyError."""

    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')

    return True


def get_insert_columns(columns: list[Column]) -> list[Column]:
    """Возвращает столбцы, значения которых вводит пользователь, без ID."""

    insert_columns = []

    for name, type_ in columns:
        if name != ID_COLUMN:
            insert_columns.append((name, type_))

    return insert_columns


def check_values_count(columns: list[Column], values: list[str | int | bool]) -> bool:
    """Проверяет, что для каждого столбца передано одно значение."""

    if len(values) != len(columns):
        raise ValueError(
            f"Ожидалось значений: {len(columns)}, "
            f"получено: {len(values)}"
        )

    return True


def check_values_types(columns: list[Column], values: list[str | int | bool]) -> bool:
    """Проверяет соответствие типов значений типам столбцов."""

    for index in range(len(columns)):
        name, type_ = columns[index]
        value = values[index]
        if type_ == "int":
            valid = isinstance(value, int) and not isinstance(value, bool)
        elif type_ == "str":
            valid = isinstance(value, str)
        elif type_ == "bool":
            valid = isinstance(value, bool)
        else:
            valid = False

        if not valid:
            raise ValueError(f'{value}. Столбец "{name}" должен иметь тип {type_}')

    return True


def generate_record_id(table_data: list[dict]) -> int:
    """Возвращает максимальный ID существующих записей плюс один."""

    max_id = 0

    for record in table_data:
        if record[ID_COLUMN] > max_id:
            max_id = record[ID_COLUMN]

    return max_id + 1


def create_record(
    columns: list[Column], values: list[str | int | bool], record_id: int
) -> dict:
    """Создает словарь записи из ID, столбцов и значений."""

    record = {ID_COLUMN: record_id}

    for index in range(len(columns)):
        name = columns[index][0]
        record[name] = values[index]

    return record


@handle_db_errors
@log_time
def insert(
    metadata: dict, table_name: str, values: list[str | int | bool]
) -> list[dict] | None:
    """Добавляет запись и возвращает данные таблицы; при ошибке возвращает None."""

    table_exists(metadata, table_name)

    columns = get_insert_columns(metadata[table_name]["columns"])

    check_values_count(columns, values)
    check_values_types(columns, values)

    table_data = load_table_data(table_name)
    record_id = generate_record_id(table_data)
    record = create_record(columns, values, record_id)
    table_data.append(record)

    return table_data


def record_matches(record: dict, where_clause: dict[str, str | int | bool]) -> bool:
    """Проверяет, совпадают ли значения записи со всеми условиями."""

    for column, value in where_clause.items():
        if column not in record or record[column] != value:
            return False

    return True


@handle_db_errors
@log_time
def select(
    table_data: list[dict],
    where_clause: dict[str, str | int | bool] | None = None,
) -> list[dict] | None:
    """Возвращает все записи при where_clause is None или записи по условию."""

    if where_clause is None:
        return table_data

    selected_records = []

    for record in table_data:
        if record_matches(record, where_clause):
            selected_records.append(record)

    return selected_records


def update_record(record: dict, set_clause: dict[str, str | int | bool]) -> dict:
    """Изменяет поля одной записи согласно переданным значениям."""

    for column, value in set_clause.items():
        record[column] = value

    return record


@handle_db_errors
def update(
    table_data: list[dict],
    set_clause: dict[str, str | int | bool],
    where_clause: dict[str, str | int | bool],
) -> list[dict] | None:
    """Обновляет записи по условию и возвращает измененные данные таблицы."""

    for record in table_data:
        if record_matches(record, where_clause):
            update_record(record, set_clause)

    return table_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(
    table_data: list[dict], where_clause: dict[str, str | int | bool]
) -> list[dict] | None:
    """Возвращает список записей, оставшихся после удаления по условию."""

    remaining_records = []

    for record in table_data:
        if not record_matches(record, where_clause):
            remaining_records.append(record)

    return remaining_records
