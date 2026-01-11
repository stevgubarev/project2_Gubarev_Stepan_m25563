VALID_TYPES = {"int", "str", "bool"}
ID_COL = ("ID", "int")


def cast_value(raw: str, expected_type: str):
    """Cast raw string into int/str/bool according to schema."""
    if expected_type == "str":
        return str(raw)

    if expected_type == "int":
        try:
            return int(raw)
        except ValueError as e:
            raise ValueError(f"Некорректное значение: {raw}. Попробуйте снова.") from e

    if expected_type == "bool":
        low = str(raw).strip().lower()
        if low in {"true", "1", "yes", "y"}:
            return True
        if low in {"false", "0", "no", "n"}:
            return False
        raise ValueError(f"Некорректное значение: {raw}. Попробуйте снова.")

    raise ValueError(f"Некорректное значение: {raw}. Попробуйте снова.")


def _schema_map(schema: list[dict]) -> dict[str, str]:
    return {c["name"]: c["type"] for c in schema}


def create_table(metadata: dict, table_name: str, columns: list[tuple[str, str]]) -> dict:
    """Create table metadata. Adds ID:int automatically as first column."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    full_columns = [ID_COL, *columns]

    for col_name, col_type in full_columns:
        if col_type not in VALID_TYPES:
            print(f"Некорректное значение: {col_name}:{col_type}. Попробуйте снова.")
            return metadata

    metadata[table_name] = [{"name": n, "type": t} for n, t in full_columns]
    cols_text = ", ".join([f"{c['name']}:{c['type']}" for c in metadata[table_name]])
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_text}')
    return metadata


def drop_table(metadata: dict, table_name: str) -> dict:
    """Drop table from metadata."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata: dict) -> None:
    """Print list of tables."""
    if not metadata:
        print("Таблиц нет.")
        return

    for name in sorted(metadata.keys()):
        print(f"- {name}")


def insert(metadata: dict, table_name: str, table_data: list[dict], values_raw: list[str]) -> list[dict]:
    """Insert row into table_data. values_raw does not include ID."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return table_data

    schema = metadata[table_name]
    cols = [c["name"] for c in schema]
    types = _schema_map(schema)

    expected = len(cols) - 1
    if len(values_raw) != expected:
        print(f"Некорректное значение: ожидается {expected} значений. Попробуйте снова.")
        return table_data

    new_id = 1
    if table_data:
        new_id = max(int(r.get("ID", 0)) for r in table_data) + 1

    row: dict = {"ID": new_id}
    idx = 0
    for col in cols:
        if col == "ID":
            continue
        row[col] = cast_value(values_raw[idx], types[col])
        idx += 1

    table_data.append(row)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def select_rows(schema: list[dict], table_data: list[dict], where_clause: dict | None = None) -> list[dict]:
    """Return rows filtered by typed where_clause."""
    if where_clause is None:
        return list(table_data)

    (col, val), = where_clause.items()
    if col not in {c["name"] for c in schema}:
        print(f"Ошибка: Таблица или столбец {col} не найден.")
        return []

    return [row for row in table_data if row.get(col) == val]


def update_rows(
    schema: list[dict],
    table_data: list[dict],
    set_clause: dict,
    where_clause: dict,
) -> tuple[list[dict], list[int]]:
    """Update rows and return (data, updated_ids). Clauses are typed."""
    (wcol, wval), = where_clause.items()
    (scol, sval), = set_clause.items()

    cols = {c["name"] for c in schema}
    if wcol not in cols:
        print(f"Ошибка: Таблица или столбец {wcol} не найден.")
        return table_data, []
    if scol not in cols:
        print(f"Ошибка: Таблица или столбец {scol} не найден.")
        return table_data, []
    if scol == "ID":
        print("Некорректное значение: нельзя менять ID. Попробуйте снова.")
        return table_data, []

    updated: list[int] = []
    for row in table_data:
        if row.get(wcol) == wval:
            row[scol] = sval
            updated.append(int(row.get("ID", 0)))

    return table_data, updated


def delete_rows(schema: list[dict], table_data: list[dict], where_clause: dict) -> tuple[list[dict], list[int]]:
    """Delete rows and return (new_data, deleted_ids). Clause is typed."""
    (wcol, wval), = where_clause.items()

    cols = {c["name"] for c in schema}
    if wcol not in cols:
        print(f"Ошибка: Таблица или столбец {wcol} не найден.")
        return table_data, []

    kept: list[dict] = []
    deleted: list[int] = []
    for row in table_data:
        if row.get(wcol) == wval:
            deleted.append(int(row.get("ID", 0)))
        else:
            kept.append(row)

    return kept, deleted

