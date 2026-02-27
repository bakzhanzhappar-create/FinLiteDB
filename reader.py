import json


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
