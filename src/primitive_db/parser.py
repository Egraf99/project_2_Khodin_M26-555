"""Разбор значений и условий пользовательских команд."""

import shlex

from primitive_db.decorators import handle_db_errors


def split_arguments(text: str) -> list[str]:
    """Разделяет текст на значения, запятые, скобки и знаки равенства."""

    lexer = shlex.shlex(text, posix=False, punctuation_chars="(),=")
    lexer.whitespace_split = True
    lexer.commenters = ""

    return list(lexer)


def parse_value(value: str) -> str | int | bool:
    """Преобразует текст в строку в кавычках, целое число или bool."""

    value = value.strip()

    if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
        parts = shlex.split(value)
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

    raise ValueError(value)


def parse_values(text: str) -> list[str | int | bool]:
    """Разбирает значения в скобках, разделенные запятыми, для insert."""

    text = text.strip()

    if not text.startswith("(") or not text.endswith(")"):
        raise ValueError(text)

    parts = split_arguments(text[1:-1])

    if not parts:
        return []

    if len(parts) % 2 == 0:
        raise ValueError(text)

    values = []

    for index in range(len(parts)):
        if index % 2 == 1:
            if parts[index] != ",":
                raise ValueError(text)
        else:
            value = parse_value(parts[index])
            values.append(value)

    return values


def parse_where(text: str) -> dict[str, str | int | bool]:
    """Разбирает пары столбец = значение для where и set."""

    parts = split_arguments(text)

    if not parts or len(parts) % 4 != 3:
        raise ValueError(text)

    conditions = {}

    for index in range(0, len(parts), 4):
        column = parts[index]
        if column in (",", "=") or parts[index + 1] != "=":
            raise ValueError(text)
        if index + 3 < len(parts) and parts[index + 3] != ",":
            raise ValueError(text)
        value = parse_value(parts[index + 2])
        conditions[column] = value

    return conditions


@handle_db_errors
def parse_command(user_input: str) -> list[str] | None:
    """Разбирает команду и выводит сообщение при незакрытых кавычках."""

    return shlex.split(user_input)
