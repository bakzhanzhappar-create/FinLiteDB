import json


def run_fifo(amount, username):
    filename = f"{username}.json"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            db = json.load(f)
    except:
        return 0

    templates = [k for k in db.keys() if k != "piggybanks"]
    if not templates:
        print("База шаблонов пуста.")
        return amount

    print("Доступные шаблоны:", templates)
    name = input("Выберите шаблон для расчета: ")
    if name not in db:
        print("Шаблон не найден.")
        return amount

    rules_f, rules_p = db[name]
    initial_sum = float(amount)
    current_balance = initial_sum
    history = []
    fail_idx = None

    for i in range(len(rules_f)):
        f_val, f_desc = rules_f[i]
        p_val, p_desc = rules_p[i]

        # 1. Фикс
        if f_val != 0:
            current_balance -= f_val
            history.append(f"{i + 1} Фикс: -{f_val} ({f_desc})")
            if current_balance < 0 and fail_idx is None: fail_idx = i + 1

        # 2. Процент от ПЕРВОНАЧАЛЬНОЙ суммы
        if p_val != 0:
            deduction = initial_sum * (p_val / 100)
            current_balance -= deduction
            history.append(f"{i + 1} Проц: -{p_val}% [-{round(deduction, 2)}] ({p_desc})")
            if current_balance < 0 and fail_idx is None: fail_idx = i + 1

    print("\n" + "=" * 40)
    if fail_idx:
        print(f"ВНИМАНИЕ: Не хватило! Начиная с правила номер {fail_idx}")
    else:
        print("СТАТУС: Денег хватило на всё.")

    print(f"ИТОГОВЫЙ ОСТАТОК: {round(current_balance, 2)}")
    print("-" * 40)
    for line in history: print(line)
    print("=" * 40 + "\n")

    return current_balance
