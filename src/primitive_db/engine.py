import shlex

import prompt
from prettytable import PrettyTable

from src.primitive_db.core import (
    cast_value,
    create_table,
    delete_rows,
    drop_table,
    insert,
    list_tables,
    select_rows,
    update_rows,
)
from src.primitive_db.parser import parse_clause, parse_values
from src.primitive_db.utils import META_FILE, load_metadata, load_table_data, save_metadata, save_table_data


def print_help() -> None:
    print("\n***Операции с данными***\n")
    print("Таблицы:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> ... - создать таблицу")
    print("<command> list_tables - показать список таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу\n")

    print("CRUD:")
    print('<command> insert into <имя_таблицы> values ("text", 1, true) - создать запись')
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print("<command> select from <имя_таблицы> where <col> = <val> - прочитать по условию")
    print("<command> update <имя_таблицы> set <col> = <val> where <col> = <val> - обновить")
    print("<command> delete from <имя_таблицы> where <col> = <val> - удалить\n")

    print("Общие команды:")
    print("<command> exit - выход")
    print("<command> help - справка\n")


def _print_table(schema: list[dict], rows: list[dict]) -> None:
    t = PrettyTable()
    columns = [c["name"] for c in schema]
    t.field_names = columns
    for r in rows:
        t.add_row([r.get(col) for col in columns])
    print(t)


def welcome() -> None:
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

        if not args:
            continue

        cmd = args[0]
        metadata = load_metadata(META_FILE)

        # ---------- TABLES ----------
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

        # ---------- INSERT ----------
        if len(args) >= 4 and args[0] == "insert" and args[1] == "into":
            table_name = args[2]
            low = user_input.lower()
            idx = low.find(" values ")
            if idx == -1:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            values_part = user_input[idx + len(" values "):].strip()
            try:
                values_raw = parse_values(values_part)
            except ValueError as e:
                print(str(e))
                continue

            table_data = load_table_data(table_name)
            new_data = insert(metadata, table_name, table_data, values_raw)
            save_table_data(table_name, new_data)
            continue

        # ---------- SELECT ----------
        if len(args) >= 3 and args[0] == "select" and args[1] == "from":
            table_name = args[2]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            schema = metadata[table_name]
            table_data = load_table_data(table_name)

            where_typed = None
            if len(args) > 3:
                if args[3] != "where":
                    print(f"Функции {cmd} нет. Попробуйте снова.")
                    continue
                where_text = user_input.split(" where ", 1)[1].strip()
                try:
                    raw_where = parse_clause(where_text)
                except ValueError as e:
                    print(str(e))
                    continue

                types = {c["name"]: c["type"] for c in schema}
                (col, raw_val), = raw_where.items()
                if col not in types:
                    print(f"Ошибка: Таблица или столбец {col} не найден.")
                    continue
                where_typed = {col: cast_value(raw_val, types[col])}

            rows = select_rows(schema, table_data, where_typed)
            _print_table(schema, rows)
            continue

        # ---------- UPDATE ----------
        if len(args) >= 2 and args[0] == "update":
            table_name = args[1]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            schema = metadata[table_name]

            low = user_input.lower()
            idx_set = low.find(" set ")
            idx_where = low.find(" where ")
            if idx_set == -1 or idx_where == -1 or idx_where < idx_set:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            set_text = user_input[idx_set + len(" set "):idx_where].strip()
            where_text = user_input[idx_where + len(" where "):].strip()

            try:
                raw_set = parse_clause(set_text)
                raw_where = parse_clause(where_text)
            except ValueError as e:
                print(str(e))
                continue

            types = {c["name"]: c["type"] for c in schema}
            (scol, sraw), = raw_set.items()
            (wcol, wraw), = raw_where.items()

            if scol not in types:
                print(f"Ошибка: Таблица или столбец {scol} не найден.")
                continue
            if wcol not in types:
                print(f"Ошибка: Таблица или столбец {wcol} не найден.")
                continue

            set_typed = {scol: cast_value(sraw, types[scol])}
            where_typed = {wcol: cast_value(wraw, types[wcol])}

            table_data = load_table_data(table_name)
            new_data, ids = update_rows(schema, table_data, set_typed, where_typed)
            save_table_data(table_name, new_data)

            if len(ids) == 1:
                print(f'Запись с ID={ids[0]} в таблице "{table_name}" успешно обновлена.')
            elif len(ids) > 1:
                print(f'Обновлено записей: {len(ids)} в таблице "{table_name}".')
            else:
                print("Записи не найдены.")
            continue

        # ---------- DELETE ----------
        if len(args) >= 4 and args[0] == "delete" and args[1] == "from":
            table_name = args[2]
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue

            schema = metadata[table_name]
            if " where " not in user_input.lower():
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            where_text = user_input.split(" where ", 1)[1].strip()
            try:
                raw_where = parse_clause(where_text)
            except ValueError as e:
                print(str(e))
                continue

            types = {c["name"]: c["type"] for c in schema}
            (wcol, wraw), = raw_where.items()
            if wcol not in types:
                print(f"Ошибка: Таблица или столбец {wcol} не найден.")
                continue

            where_typed = {wcol: cast_value(wraw, types[wcol])}

            table_data = load_table_data(table_name)
            new_data, ids = delete_rows(schema, table_data, where_typed)
            save_table_data(table_name, new_data)

            if len(ids) == 1:
                print(f'Запись с ID={ids[0]} успешно удалена из таблицы "{table_name}".')
            elif len(ids) > 1:
                print(f'Удалено записей: {len(ids)} из таблицы "{table_name}".')
            else:
                print("Записи не найдены.")
            continue

        print(f"Функции {cmd} нет. Попробуйте снова.")

