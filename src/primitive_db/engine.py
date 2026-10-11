"""Модуль отвечает за запуск, цикл и разбор команд пользователя."""

import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.core import (
    Column,
    check_values_types,
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    table_exists,
    update,
)
from primitive_db.parser import parse_values, parse_where, split_arguments
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help() -> None:
    """Выводит справку по доступным командам."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> insert into <таблица> values (<значения>) - добавить запись")
    print("<command> select from <таблица> [where <условие>] - показать записи")
    print("<command> update <таблица> set <значения> where <условие> - обновить")
    print("<command> delete from <таблица> where <условие> - удалить записи")
    print("<command> info <таблица> - информация о таблице")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def handle_exit(args: list[str], user_input: str) -> bool:
    """Выход из программы."""

    if len(args) != 1:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return True

    return False


def handle_help(args: list[str], user_input: str) -> bool:
    """Показывает справку."""

    if len(args) != 1:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return True

    print_help()

    return True


def handle_list_tables(metadata: dict, args: list[str], user_input: str) -> bool:
    """Выводит список таблиц."""

    if len(args) != 1:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return True

    tables = list_tables(metadata)

    for table_name in tables:
        print(f"- {table_name}")

    if not tables:
        print("Таблиц пока нет.")

    return True


def handle_create_table(
    metadata: dict, args: list[str], user_input: str, filepath: str
) -> bool:
    """Создает новую таблицу."""

    if len(args) < 3 or not args[1]:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return True

    table_name = args[1]
    columns = []

    for column in args[2:]:
        parts = column.split(":")
        if len(parts) != 2 or not parts[0] or not parts[1]:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return True
        columns.append((parts[0], parts[1]))

    existed = table_name in metadata
    metadata = create_table(metadata, table_name, columns)
    save_metadata(filepath, metadata)

    if not existed and table_name in metadata:
        description = ", ".join(
            f"{name}:{type_}" for name, type_ in metadata[table_name]["columns"]
        )
        print(
            f'Таблица "{table_name}" успешно создана '
            f"со столбцами: {description}"
        )

    return True


def handle_drop_table(
    metadata: dict, args: list[str], user_input: str, filepath: str
) -> bool:
    """Удаление таблицы."""

    if len(args) != 2 or not args[1]:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return True

    table_name = args[1]
    existed = table_name in metadata
    metadata = drop_table(metadata, table_name)
    save_metadata(filepath, metadata)

    if existed and table_name not in metadata:
        print(f'Таблица "{table_name}" успешно удалена.')

    return True


def check_clause(
    columns: list[Column], clause: dict[str, str | int | bool]
) -> bool:
    """Проверяет существование столбцов и типы значений в where или set."""

    clause_columns = []
    values = []

    for name, value in clause.items():
        found = False
        for column_name, type_ in columns:
            if column_name == name:
                clause_columns.append((name, type_))
                values.append(value)
                found = True
                break
        if not found:
            print(f'Некорректное значение: столбец "{name}". Попробуйте снова.')
            return False

    return check_values_types(clause_columns, values)


def print_table(columns: list[Column], table_data: list[dict]) -> None:
    """Выводит записи таблицы с помощью PrettyTable."""

    names = []

    for name, type_ in columns:
        names.append(name)

    table = PrettyTable()
    table.field_names = names

    for record in table_data:
        values = []
        for name in names:
            values.append(record[name])
        table.add_row(values)

    print(table)


def handle_insert(metadata: dict, args: list[str], user_input: str) -> bool:
    """Разбирает команду insert, добавляет запись и сохраняет данные."""

    if len(args) < 5 or args[1] != "into" or args[3] != "values":
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return True

    table_name = shlex.split(args[2])[0]
    values = parse_values(" ".join(args[4:]))

    if values is None:
        return True

    table_data = insert(metadata, table_name, values)

    if table_data is not None:
        save_table_data(table_name, table_data)
        record_id = table_data[-1]["ID"]
        print(f'Запись с ID={record_id} добавлена в таблицу "{table_name}".')

    return True


def handle_select(metadata: dict, args: list[str], user_input: str) -> bool:
    """Разбирает команду select и выводит выбранные записи."""

    if len(args) < 3 or args[1] != "from":
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return True

    table_name = shlex.split(args[2])[0]

    if not table_exists(metadata, table_name):
        return True

    columns = metadata[table_name]["columns"]
    where_clause = None

    if len(args) > 3:
        if args[3] != "where":
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            return True
        where_clause = parse_where(" ".join(args[4:]))
        if where_clause is None or not check_clause(columns, where_clause):
            return True

    table_data = load_table_data(table_name)
    selected_records = select(table_data, where_clause)
    print_table(columns, selected_records)

    return True


def handle_update(metadata: dict, args: list[str], user_input: str) -> bool:
    """Разбирает команду update, обновляет записи и сохраняет данные."""

    if len(args) < 4 or args[2] != "set" or "where" not in args[3:]:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return True

    table_name = shlex.split(args[1])[0]

    if not table_exists(metadata, table_name):
        return True

    where_index = args.index("where", 3)
    set_clause = parse_where(" ".join(args[3:where_index]))
    where_clause = parse_where(" ".join(args[where_index + 1:]))

    if set_clause is None or where_clause is None:
        return True

    columns = metadata[table_name]["columns"]

    if not check_clause(columns, set_clause):
        return True

    if not check_clause(columns, where_clause):
        return True

    table_data = load_table_data(table_name)
    matched_records = select(table_data, where_clause)

    if not matched_records:
        print("Подходящих записей нет.")
        return True

    table_data = update(table_data, set_clause, where_clause)
    save_table_data(table_name, table_data)

    for record in matched_records:
        print(f'Запись с ID={record["ID"]} в таблице "{table_name}" обновлена.')

    return True


def handle_delete(metadata: dict, args: list[str], user_input: str) -> bool:
    """Разбирает команду delete, удаляет записи и сохраняет данные."""

    if len(args) < 5 or args[1] != "from" or args[3] != "where":
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return True

    table_name = shlex.split(args[2])[0]

    if not table_exists(metadata, table_name):
        return True

    where_clause = parse_where(" ".join(args[4:]))

    if where_clause is None:
        return True

    columns = metadata[table_name]["columns"]

    if not check_clause(columns, where_clause):
        return True

    table_data = load_table_data(table_name)
    matched_records = select(table_data, where_clause)

    if not matched_records:
        print("Подходящих записей нет.")
        return True

    table_data = delete(table_data, where_clause)
    save_table_data(table_name, table_data)

    for record in matched_records:
        print(f'Запись с ID={record["ID"]} удалена из таблицы "{table_name}".')

    return True


def handle_info(metadata: dict, args: list[str], user_input: str) -> bool:
    """Выводит имя таблицы, ее столбцы и количество записей."""

    if len(args) != 2:
        print(f"Некорректное значение: {user_input}. Попробуйте снова.")
        return True

    table_name = args[1]

    if not table_exists(metadata, table_name):
        return True

    columns = metadata[table_name]["columns"]
    description = ", ".join(f"{name}:{type_}" for name, type_ in columns)

    table_data = load_table_data(table_name)

    print(f"Таблица: {table_name}")
    print(f"Столбцы: {description}")
    print(f"Количество записей: {len(table_data)}")

    return True


def run() -> None:
    """Запускает цикл управления таблицами с сохранением метаданных в JSON."""

    filepath = "db_meta.json"
    print_help()

    while True:
        metadata = load_metadata(filepath)
        user_input = prompt.string("Введите команду: ")

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0]
        if command == "exit":
            if not handle_exit(args, user_input):
                break
        elif command == "help":
            handle_help(args, user_input)
        elif command == "list_tables":
            handle_list_tables(metadata, args, user_input)
        elif command == "create_table":
            handle_create_table(metadata, args, user_input, filepath)
        elif command == "drop_table":
            handle_drop_table(metadata, args, user_input, filepath)
        elif command in ("insert", "select", "update", "delete"):
            args = split_arguments(user_input)
            if args is None:
                continue
            if command == "insert":
                handle_insert(metadata, args, user_input)
            elif command == "select":
                handle_select(metadata, args, user_input)
            elif command == "update":
                handle_update(metadata, args, user_input)
            elif command == "delete":
                handle_delete(metadata, args, user_input)
        elif command == "info":
            handle_info(metadata, args, user_input)
        else:
            print(f"Функции {command} нет. Попробуйте снова.")
