VALID_TYPES = {"int", "str", "bool"}
ID_COL = ("ID", "int")


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

