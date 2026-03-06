#обязанности у этого модуля:
#Чтение и запись json-а

import json

#чтение. To storage_test.py from app.py
def get_user_db(username):
    """Читает JSON пользователя. Возвращает dict или None."""
    filename = f"{username}.json"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

#запись. To storage_test.py from app.py
def write_user_db(username, data):
    """Записывает данные в JSON пользователя."""
    filename = f"{username}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

#Чтение и десериализация из JSON файла. Почти такой же но чуть различается. To storage_test.py from reader.py
def show_database(username):
    filename = f"{username}.json"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            db = json.load(f)
    except:
        print("База пуста.")
        return

    print(f"\n--- БАЗА ПОЛЬЗОВАТЕЛЯ: {username} ---")
    templates = {k: v for k, v in db.items() if k != "piggybanks"}

    if not templates:
        print("Шаблонов пока нет.")
    else:
        for name, rules in templates.items():
            f_list, p_list = rules
            act_f = len([x for x in f_list if x[0] > 0])
            act_p = len([x for x in p_list if x[0] > 0])
            print(f"\n Шаблон: {name} (фиксов:{act_f}, проц:{act_p})")
            for i in range(len(f_list)):
                if f_list[i][0] > 0: print(f"  - Фикс: {f_list[i][0]} ({f_list[i][1]})")
                if p_list[i][0] > 0: print(f"  - Проц: {p_list[i][0]}% ({p_list[i][1]})")
# --------------------------------------------------------------

#To storage_test from dealer_input
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
