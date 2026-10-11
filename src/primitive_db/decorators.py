"""Декораторы для обработки ошибок базы данных."""

from collections.abc import Callable
from functools import wraps
from typing import Any


def handle_db_errors(function: Callable[..., Any]) -> Callable[..., Any]:
    """Выводит сообщение об ошибке и возвращает None вместо исключения."""

    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Вызывает функцию и обрабатывает ошибки файлов, ключей и значений."""

        try:
            return function(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден.")
        except KeyError as error:
            print(f"Ошибка: {error.args[0]}")
        except ValueError as error:
            print(f"Некорректное значение: {error}. Попробуйте снова.")
        except NotImplementedError as error:
            print(f"Функции {error.args[0]} нет. Попробуйте снова.")

        return None

    return wrapper
