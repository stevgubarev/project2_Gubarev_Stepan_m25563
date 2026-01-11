import prompt


def welcome() -> None:
    """Print welcome screen and run minimal command loop (help/exit)."""
    while True:
        print("\n***")
        print("<command> exit - выйти из программы")
        print("<command> help - справочная информация")

        cmd = prompt.string("Введите команду: ").strip()

        if cmd == "exit":
            return
        if cmd == "help":
            # help уже напечатали выше, просто повторяем цикл
            continue

        print(f"Функции {cmd} нет. Попробуйте снова.")

