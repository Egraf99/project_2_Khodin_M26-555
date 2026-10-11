"""Модуль отвечает за запуск, цикл и разбор команд пользователя."""

import shlex

import prompt

from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.utils import load_metadata, save_metadata


def print_help():
    """Выводит справку по доступным командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
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


def run():
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
        else:
            print(f"Функции {command} нет. Попробуйте снова.")
