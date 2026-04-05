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
    Сохранение шаблона: список правил в порядке FIFO.
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


template_name_variable=list()
fix_number_list=list()
fix_description_list=list()
percent_number_list=list()
percent_description_list=list()

def hello():
    try:
        deal=str(input(" <<add>> add new template \n <<convert>> to convert into JSON storage\n <<read>> to show what is written in JSON storage \n <<exit>> to finish programme \n"))
        return deal
    except ValueError:
        print("Something went wrong")
        return None

def message_positive():
    print("\n--- Success! ---\n")

def message_negative():
    print("\nSomething went wrong\n")

def template_name():
    try:
        template_name_variable=str(input("Enter template name: "))
        return template_name_variable
    except ValueError:
        message_negative()
        return None

def fix():
    try:
        fix_number_list=int(input("Enter how much u need to write off from amount: "))
        return fix_number_list
    except ValueError:
        message_negative()
        print("Use only whole number!")
        return fix()

def fix_description():
    try:
        fix_description_list=str(input("Enter a description for the fix: "))
        return fix_description_list
    except ValueError:
        message_negative()
        return None

def percentage():
    try:
        percent_number_list=int(input("Enter how much u need to write off from amount by percentage: "))
        return percent_number_list
    except ValueError:
        message_negative()
        print("Use only whole number!")
        return percentage()

def percentage_description():
    try:
        percentage_description_list=str(input("Enter a description for the percentage: "))
        return percentage_description_list
    except ValueError:
        message_negative()
        return None

def full_list_append():
    try:
        template_name_variable.append(template_name())
        while True:
            ask = str(input("What do you wish to start input?\n(f/p)\nIf u sure for results write <<b>>: "))
            if ask=='p':
                percent_number_list.append(percentage())
                percent_description_list.append(percentage_description())
            if ask=='f':
                fix_number_list.append(fix())
                fix_description_list.append(fix_description())
            elif ask=='b':
                break
    except ValueError:
            message_negative()
            return None