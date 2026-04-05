import json

import user_records


def run_fifo(amount, username, template_name=None):
    """
    При template_name — возвращает (remainder, history, fail_idx).
    Без template_name — консольный режим, возвращает remainder (float).
    """
    filename = f"{username}.json"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            db = json.load(f)
    except Exception:
        return (float(amount), [], None) if template_name is not None else 0

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
    if isinstance(raw, list) and raw and isinstance(raw[0], dict) and raw[0].get("type") in ("f", "p"):
        rules_ordered = raw
    else:
        rules_f, rules_p = raw
        rules_ordered = []
        for i in range(max(len(rules_f), len(rules_p))):
            row_f = rules_f[i] if i < len(rules_f) else [0, "пусто"]
            row_p = rules_p[i] if i < len(rules_p) else [0, "пусто"]
            f_val, f_desc = row_f[0], row_f[1]
            if f_val != 0:
                rules_ordered.append({"type": "f", "val": f_val, "desc": f_desc})
            p_val, p_desc = row_p[0], row_p[1]
            if p_val != 0:
                rules_ordered.append({"type": "p", "val": p_val, "desc": p_desc})

    initial_sum = float(amount)
    current_balance = initial_sum
    history = []
    fail_idx = None

    for i, r in enumerate(rules_ordered):
        step = i + 1
        if r.get("type") == "f":
            val = r.get("val", 0)
            desc = r.get("desc", "")
            current_balance -= val
            history.append(f"{step} Фикс: -{val} ({desc})")
            if current_balance < 0 and fail_idx is None:
                fail_idx = step
        elif r.get("type") == "p":
            val = r.get("val", 0)
            desc = r.get("desc", "")
            deduction = initial_sum * (val / 100)
            current_balance -= deduction
            history.append(f"{step} Проц: -{val}% [-{round(deduction, 2)}] ({desc})")
            if current_balance < 0 and fail_idx is None:
                fail_idx = step

    rounded = round(current_balance, 2)

    user_records.log_fifo_use(username, name, initial_sum, rounded, fail_idx, history)

    if template_name is not None:
        return (rounded, history, fail_idx)

    print("\n" + "=" * 40)
    if fail_idx:
        print(f"ВНИМАНИЕ: Не хватило! Начиная с правила номер {fail_idx}")
    else:
        print("СТАТУС: Денег хватило на всё.")
    print(f"ИТОГОВЫЙ ОСТАТОК: {rounded}")
    print("-" * 40)
    for line in history:
        print(line)
    print("=" * 40 + "\n")
    return rounded


#calculator
def calculate(summ):
    try:
        with open("template_storage.json", 'r', encoding='utf-8') as f:
            template_dict = json.load(f)

        for names in template_dict.keys():
            print(names)

        name = str(input("\nEnter template name to apply: "))

        if name in template_dict:
            fix_val = template_dict[name][0][0]
            per_val = template_dict[name][1][0]

            print(f"Template found: Fix={fix_val}, Percent={per_val}%")
            choice = input("Apply (f)ix or (p)ercent? ")

            if choice == 'f':
                result = summ - fix_val
            else:
                result = summ - (summ * per_val / 100)
            return result

        else:
            print(f"Template '{name}' not found!")
            return None

    except FileNotFoundError:
        print("File not found")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None