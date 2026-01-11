import time


def handle_db_errors(func):
    """Centralized exception handler for DB functions."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                  "Ошибка: Файл данных не найден. Возможно, база данных "
                  "не инициализирована."
            )
            return None
        except KeyError as e:
            missing = e.args[0] if e.args else "?"
            print(f"Ошибка: Таблица или столбец {missing} не найден.")
            return None
        except ValueError as e:
            # ValueError messages in this project are user-facing already
            print(str(e))
            return None

    return wrapper


def confirm_action(action_name: str):
    """Decorator factory: asks confirmation for dangerous actions."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            ).strip().lower()
            if answer != "y":
                print("Операция отменена.")
                # возвращаем "старые данные", чтобы ничего не сломать
                return args[0] if args else None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Print execution time of function."""

    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result

    return wrapper


def create_cacher():
    """
    Closure-based cacher.
    cache_result(key, value_func): returns cached value by key
    or computes and stores it.
    """
    cache: dict = {}

    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        value = value_func()
        cache[key] = value
        return value

    return cache_result

