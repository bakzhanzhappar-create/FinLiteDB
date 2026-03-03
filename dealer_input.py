#обязанности у этого модуля:
#бъединить с auth.py, app.py, dealer_input
#Строго IO и веб интерфейс функционал

import json


def hello():
    return input(
        "\n <<add>> создать шаблон \n <<read>> база данных \n <<interact>> расчет FIFO \n <<bank>> создать копилку \n <<exit>> выход \n").lower()


def full_list_save(username):
    """Сбор данных и моментальная запись в JSON пользователя"""
    name = input("Введите имя нового шаблона: ").strip()
    filename = f"{username}.json"

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            db = json.load(f)
    except:
        db = {}

    if name in db:
        print(f"!!! Ошибка: Шаблон '{name}' уже существует в вашей базе.")
        return

    fixes, percs = [], []
    while True:
        ask = input(f"[{name}] Добавить (f)икс, (p)роцент или (s)охранить всё?: ").lower()
        if ask == 'f':
            val = int(input("Сумма вычета: "))
            desc = input("Описание фикса: ")
            fixes.append([val, desc])
        elif ask == 'p':
            val = int(input("Процент (0-100): "))
            if val > 100: val = 100
            desc = input("Описание процента: ")
            percs.append([val, desc])
        elif ask == 's':
            break

    # Валидатор "воздуха": выравниваем списки до одинаковой длины
    max_len = max(len(fixes), len(percs))
    if max_len == 0:
        print("Пустой шаблон не сохранен.")
        return

    while len(fixes) < max_len: fixes.append([0, "пусто"])
    while len(percs) < max_len: percs.append([0, "пусто"])

    # Заливаем в базу
    db[name] = [fixes, percs]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    print(f"--- Шаблон '{name}' успешно сохранен ---")


def save_template(username, name, rules):
    """
    Сохранение шаблона: один список правил в порядке добавления (FIFO).
    rules: [{"type": "f"|"p", "val": число, "desc": строка}, ...]
    """
    filename = f"{username}.json"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            db = json.load(f)
    except Exception:
        db = {}

    if name in db:
        return False, f"Шаблон '{name}' уже существует."

    if not rules:
        return False, "Пустой шаблон не сохранен."

    db[name] = list(rules)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    return True, None
