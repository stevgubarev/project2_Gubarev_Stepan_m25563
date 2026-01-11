import shlex


def _strip_parens(text: str) -> str:
    text = text.strip()
    if text.startswith("(") and text.endswith(")"):
        return text[1:-1].strip()
    raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")


def _split_csv(text: str) -> list[str]:
    items: list[str] = []
    buf: list[str] = []
    in_quotes = False

    for ch in text:
        if ch == '"':
            in_quotes = not in_quotes
            buf.append(ch)
            continue

        if ch == "," and not in_quotes:
            item = "".join(buf).strip()
            items.append(item)
            buf = []
            continue

        buf.append(ch)

    last = "".join(buf).strip()
    if last:
        items.append(last)
    return items


def parse_values(values_part: str) -> list[str]:
    """Parse values(<...>) into list of raw values (strings), keeping quoted text."""
    inside = _strip_parens(values_part)
    raw_items = _split_csv(inside)
    if not raw_items:
        raise ValueError(f"Некорректное значение: {values_part}. Попробуйте снова.")
    # strip outer quotes if present
    cleaned: list[str] = []
    for item in raw_items:
        item = item.strip()
        if len(item) >= 2 and item[0] == '"' and item[-1] == '"':
            cleaned.append(item[1:-1])
        else:
            cleaned.append(item)
    return cleaned


def parse_clause(text: str) -> dict[str, str]:
    """
    Parse 'col = value' into {'col': 'value'}.
    String values must be quoted in input, but shlex will remove quotes.
    """
    tokens = shlex.split(text)
    if len(tokens) < 3 or tokens[1] != "=":
        raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")
    col = tokens[0].strip()
    val = " ".join(tokens[2:]).strip()
    if not col or val == "":
        raise ValueError(f"Некорректное значение: {text}. Попробуйте снова.")
    return {col: val}

