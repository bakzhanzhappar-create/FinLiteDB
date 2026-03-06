#обязанности у этого модуля:
#создание шаблонов (фикс и проц а также их описание) и класса копилки
#грубо говоря он еще и калькулятор по этим же шаблонам и копилкам
#валидирует значения во всех этапах операции (например юзер не может в проц записать значение выше 100% или ниже 0%
#впринципе пока все
#To core.py from logic.py

import json


def run_fifo(amount, username, template_name=None):
    """
    Если template_name передан — использует его и возвращает (current_balance, history, fail_idx).
    Иначе — консольный ввод (для совместимости).
    """
#чтение файла и загрузка всех данных в локальную переменную db
    filename = f"{username}.json"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            db = json.load(f)
    except Exception:
        return (float(amount), [], None) if template_name is not None else 0
# --------------------------------------------------------------

    templates = [k for k in db.keys() if k != "piggybanks"]
    if not templates:
        if template_name is not None:
            return (float(amount), [], None)
        print("База шаблонов пуста.")
        return amount

    if template_name is not None:
        name = template_name
    else:
        print("Доступные шаблоны:", templates)
        name = input("Выберите шаблон для расчета: ")

    if name not in db:
        if template_name is not None:
            return (float(amount), [], None)
        print("Шаблон не найден.")
        return amount

    raw = db[name]
    # Новый формат: один список правил в порядке добавления (FIFO)
#isinstance() проверяет какой тип данных перед ним, после запятой стоит целевой тип данных. Если сходится то True, иначе False
#В данном случае что то вроде валидация данных перед расчетами проверяя колво f и p правил.
#Если в итоге True то данные записываются в локальную переменную rules_ordered,
#иначе начинается процедура где список с наимменьшим значением записывает недостающие значения пусто в описании а числам присвает 0

    if isinstance(raw, list) and raw and isinstance(raw[0], dict) and "type" in raw[0]:
        rules_ordered = raw
    else:
        # Старый формат [fixes, percs] — приводим к порядку: сначала все фиксы по шагам, потом проценты по шагам
        rules_f, rules_p = raw
        rules_ordered = []
        for i in range(max(len(rules_f), len(rules_p))):
            f_val, f_desc = (rules_f[i] if i < len(rules_f) else [0, "пусто"])[0], (rules_f[i] if i < len(rules_f) else [0, "пусто"])[1]
            if f_val != 0:
                rules_ordered.append({"type": "f", "val": f_val, "desc": f_desc})
            p_val = (rules_p[i] if i < len(rules_p) else [0, "пусто"])[0]
            p_desc = (rules_p[i] if i < len(rules_p) else [0, "пусто"])[1]
            if p_val != 0:
                rules_ordered.append({"type": "p", "val": p_val, "desc": p_desc})
# --------------------------------------------------------------

    initial_sum = float(amount)
    current_balance = initial_sum
    history = []
    fail_idx = None

    for i, r in enumerate(rules_ordered):
        step = i + 1
#расчет по фиксированным правилам
        if r.get("type") == "f":
            val = r.get("val", 0)
            desc = r.get("desc", "")
            current_balance -= val
            history.append(f"{step} Фикс: -{val} ({desc})")
            if current_balance < 0 and fail_idx is None:
                fail_idx = step
# --------------------------------------------------------------

#расчет по процентным правилам
        elif r.get("type") == "p":
            val = r.get("val", 0)
            desc = r.get("desc", "")
            deduction = initial_sum * (val / 100)
            current_balance -= deduction
            history.append(f"{step} Проц: -{val}% [-{round(deduction, 2)}] ({desc})")
            if current_balance < 0 and fail_idx is None:
                fail_idx = step
# --------------------------------------------------------------

    if template_name is not None:
        return (round(current_balance, 2), history, fail_idx)

    print("\n" + "=" * 40)
    if fail_idx:
        print(f"ВНИМАНИЕ: Не хватило! Начиная с правила номер {fail_idx}")
    else:
        print("СТАТУС: Денег хватило на всё.")
    print(f"ИТОГОВЫЙ ОСТАТОК: {round(current_balance, 2)}")
    print("-" * 40)
    for line in history:
        print(line)
    print("=" * 40 + "\n")
    return current_balance
