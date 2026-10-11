"""Декораторы для обработки ошибок базы данных."""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any


def handle_db_errors(function: Callable[..., Any]) -> Callable[..., Any]:
    """Выводит сообщение об ошибке и возвращает None вместо исключения."""

    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
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


def confirm_action(action_name: str) -> Callable[..., Any]:
    """Создает декоратор подтверждения действия ответом y."""

    def decorator(function: Callable[..., Any]) -> Callable[..., Any]:

        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            )
            if answer != "y":
                print("Операция отменена.")
                return None

            return function(*args, **kwargs)

        return wrapper

    return decorator


def log_time(function: Callable[..., Any]) -> Callable[..., Any]:
    """Измеряет время выполнения функции и выводит его в секундах."""

    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Вызывает функцию, выводит время и возвращает ее результат."""

        started = time.monotonic()
        result = function(*args, **kwargs)
        elapsed = time.monotonic() - started

        print(f"Функция {function.__name__} выполнилась за {elapsed:.3f} секунд")

        return result

    return wrapper


def create_cacher() -> Callable[[str, Callable[[], Any]], Any]:
    """Создает функцию, которая хранит результаты вычислений в замыкании."""

    cache: dict[str, Any] = {}

    def cache_result(key: str, value_func: Callable[[], Any]) -> Any:
        """Возвращает результат из кэша или вычисляет и сохраняет его."""

        if key not in cache:
            cache[key] = value_func()

        return cache[key]

    return cache_result
