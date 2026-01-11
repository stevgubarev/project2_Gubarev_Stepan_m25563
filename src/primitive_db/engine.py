import shlex

import prompt

from src.primitive_db.core import create_table, drop_table, list_tables
from src.primitive_db.utils import load_metadata, save_metadata

META_FILE = "db_meta.json"


def print_help() -> None:
    """Print help message."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def welcome() -> None:
    """Main loop for table management."""
    print("\n***База данных***")
    print_help()

    while True:
        user_input = prompt.string(">>>Введите команду: ").strip()
        if not user_input:
            continue

        if user_input == "exit":
            return
        if user_input == "help":
            print_help()
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        cmd = args[0]
        metadata = load_metadata(META_FILE)

        if cmd == "create_table":
            if len(args) < 3:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue
            table_name = args[1]
            raw_cols = args[2:]
            columns: list[tuple[str, str]] = []
            ok = True
            for part in raw_cols:
                if ":" not in part:
                    print(f"Некорректное значение: {part}. Попробуйте снова.")
                    ok = False
                    break
                name, typ = part.split(":", 1)
                name = name.strip()
                typ = typ.strip()
                if not name or not typ:
                    print(f"Некорректное значение: {part}. Попробуйте снова.")
                    ok = False
                    break
                columns.append((name, typ))
            if not ok:
                continue

            new_meta = create_table(metadata, table_name, columns)
            # сохраняем только если реально появилась таблица
            if new_meta != metadata or table_name in new_meta:
                save_metadata(META_FILE, new_meta)
            continue

        if cmd == "list_tables":
            list_tables(metadata)
            continue

        if cmd == "drop_table":
            if len(args) != 2:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue
            table_name = args[1]
            new_meta = drop_table(metadata, table_name)
            save_metadata(META_FILE, new_meta)
            continue

        print(f"Функции {cmd} нет. Попробуйте снова.")

