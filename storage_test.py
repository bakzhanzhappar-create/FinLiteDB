#обязанности у этого модуля:
#Чтение и запись json-а

#лазанья

import json
from presentation import no_file, empty_templates

#запись. To storage_test.py from app.py
def create_username(username):
    """Создаёт файл профиля с базовой структурой."""
    filename = f"{username}.json"
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump({"piggybanks": {}}, file, indent=4)
    return True

#чтение. To storage_test.py from app.py
def get_user_data(username):
    """Читает JSON пользователя. Возвращает dict или None."""
    filename = f"{username}.json"
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

#запись. To storage_test.py from app.py
def write_user_data(username, data):
    """Записывает данные в JSON пользователя."""
    filename = f"{username}.json"
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

#Чтение и десериализация из JSON файла. Почти такой же но чуть различается. To storage_test.py from reader.py
def show_data(username):
    filename = f"{username}.json"
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except:
        no_file()
        return

    print(f"\n--- БАЗА ПОЛЬЗОВАТЕЛЯ: {username} ---")
# лазанья
    templates = {k: v for k, v in data.items() if k != "piggybanks"}

    if not templates:
        empty_templates()
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
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception:
        data = {}

    if name in data:
        return False, f"Шаблон '{name}' уже существует."

    if not rules:
        return False, "Пустой шаблон не сохранен."

    data[name] = list(rules)
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    return True, None
