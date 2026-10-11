"""Разбор значений и условий пользовательских команд."""

import shlex


def split_arguments(text: str) -> list[str] | None:
    """Разделяет текст на значения, запятые и знаки равенства."""
    lexer = shlex.shlex(text, posix=False, punctuation_chars=",=")
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        return list(lexer)
    except ValueError:
        print(f"Некорректное значение: {text}. Попробуйте снова.")
        return None


def parse_value(value: str) -> str | int | bool | None:
    """Преобразует текст в строку в кавычках, целое число или bool."""
    value = value.strip()
    if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
        try:
            parts = shlex.split(value)
        except ValueError:
            parts = []
        if len(parts) == 1:
            return parts[0]
    elif value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    else:
        try:
            return int(value)
        except ValueError:
            pass

    print(f"Некорректное значение: {value}. Попробуйте снова.")
    return None


def parse_values(text: str) -> list[str | int | bool] | None:
    """Разбирает значения в скобках, разделенные запятыми, для insert."""
    text = text.strip()
    if not text.startswith("(") or not text.endswith(")"):
        print(f"Некорректное значение: {text}. Попробуйте снова.")
        return None

    parts = split_arguments(text[1:-1])
    if parts is None:
        return None
    if not parts:
        return []
    if len(parts) % 2 == 0:
        print(f"Некорректное значение: {text}. Попробуйте снова.")
        return None

    values = []
    for index in range(len(parts)):
        if index % 2 == 1:
            if parts[index] != ",":
                print(f"Некорректное значение: {text}. Попробуйте снова.")
                return None
        else:
            value = parse_value(parts[index])
            if value is None:
                return None
            values.append(value)
    return values


def parse_where(text: str) -> dict[str, str | int | bool] | None:
    """Разбирает пары столбец = значение для where и set."""
    parts = split_arguments(text)
    if parts is None:
        return None
    if not parts or len(parts) % 4 != 3:
        print(f"Некорректное значение: {text}. Попробуйте снова.")
        return None

    conditions = {}
    for index in range(0, len(parts), 4):
        column = parts[index]
        if column in (",", "=") or parts[index + 1] != "=":
            print(f"Некорректное значение: {text}. Попробуйте снова.")
            return None
        if index + 3 < len(parts) and parts[index + 3] != ",":
            print(f"Некорректное значение: {text}. Попробуйте снова.")
            return None
        value = parse_value(parts[index + 2])
        if value is None:
            return None
        conditions[column] = value
    return conditions
