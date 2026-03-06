#Залить коды
#обязанности у этого модуля:
#создание шаблонов (фикс и проц а также их описание) и класса копилки
#грубо говоря он еще и калькулятор по этим же шаблонам и копилкам
#валидирует значения во всех этапах операции (например юзер не может в проц записать значение выше 100% или ниже 0%
#впринципе пока все

#To core.py from app.py
#получаем словарь без копилки


#лазанья


from storage_test import *

def get_templates(username):
    """Список имён шаблонов (без piggybanks)."""
    data = get_user_data(username)
    if not data:
        return []
#проверка в одну строку ищем не является ли k "piggybanks"
#лазанья
    return [k for k in data.keys()
            if k != "piggybanks"]

#To core.py from app.py
#получаем список копилок по ключу функции get()
def get_piggybanks(username):
    """Словарь копилок пользователя."""
    data = get_user_data(username)
    if not data:
        return {}
    return data.get("piggybanks", {})

#To core.py from app.py
def delete_template(username, template_name):
    """Удаляет шаблон по имени. Возвращает True при успехе."""
    data = get_user_data(username)
    if not data or template_name not in data or template_name == "piggybanks":
        return False
    del data[template_name]
    write_user_data(username, data)
    return True

#To core.py from app.py
def delete_piggybank(username, goal_name):
    """Удаляет копилку по имени. Возвращает True при успехе."""
    data = get_user_data(username)
    if not data: return False
    pigs = data.get("piggybanks", {})
    if goal_name not in pigs: return False
    del pigs[goal_name]
    data["piggybanks"] = pigs
    write_user_data(username, data)
    return True

#класс копилки. создает копилку и там же имеет функцию переноса остатка в копилку.
# To core.py from storage.py
class PiggyBank:
    def __init__(self, username):
        self.filename = f"{username}.json"

    def _read(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except:
            return {"piggybanks": {}}

    def _write(self, data):
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def create_piggybank(self, name=None, target=None, link=None):
        if name is None:
            name = input("На что копим? (имя цели): ").strip()
        if target is None:
            target = float(input("Целевая сумма: "))
        if link is None:
            link = input("Ссылка на товар/описание: ")

        piggy_data = self._read()
        if "piggybanks" not in piggy_data:
            piggy_data["piggybanks"] = {}

        piggy_data["piggybanks"][name] = {
            "target": float(target),
            "current": 0.0,
            "link": link or ""
        }
        self._write(piggy_data)
        if name is not None and target is not None:
            return
        print(f"Копилка '{name}' активирована!")

    def deposit(self, amount, goal_name=None):
        piggy_data = self._read()
        banks = piggy_data.get("piggybanks", {})

        if not banks:
            if goal_name is not None:
                return False
            print("У вас нет активных копилок.")
            return None

        if goal_name is not None:
            choice = goal_name
        else:
            print("Ваши цели:", list(banks.keys()))
            choice = input("В какую копилку закинуть остаток?: ")

        if choice in banks:
            banks[choice]["current"] += float(amount)
            self._write(piggy_data)
            if goal_name is None:
                prog = (banks[choice]['current'] / banks[choice]['target']) * 100
                print(f"Зачислили {amount}. Прогресс '{choice}': {round(prog, 1)}%")
            return True
        return False
# --------------------------------------------------------------

#To core.py from logic.py


def run_fifo(amount, username, template_name=None):
    """
    Если template_name передан — использует его и возвращает (current_balance, history, fail_idx).
    Иначе — консольный ввод (для совместимости).
    """
#чтение файла и загрузка всех данных в локальную переменную data
    filename = f"{username}.json"
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception:
# лазанья
        return (float(amount), [], None) \
            if template_name is not None \
            else 0
# --------------------------------------------------------------

    templates = [k for k in data.keys() if k != "piggybanks"]
    if not templates:
        if template_name is not None:
            return float(amount), [], None
        print("База шаблонов пуста.")
        return amount

    if template_name is not None:
        name = template_name
    else:
        print("Доступные шаблоны:", templates)
        name = input("Выберите шаблон для расчета: ")

    if name not in data:
        if template_name is not None:
            return float(amount), [], None
        print("Шаблон не найден.")
        return amount

    raw = data[name]
    # Новый формат: один список правил в порядке добавления (FIFO)
#isinstance() проверяет какой тип данных перед ним, после запятой стоит целевой тип данных. Если сходится то True, иначе False
#В данном случае что то вроде валидация данных перед расчетами проверяя колво f и p правил.
#Если в итоге True то данные записываются в локальную переменную rules_ordered,
#иначе начинается процедура где список с наимменьшим значением записывает недостающие значения пусто в описании а числам присвает 0

    if isinstance(raw, list) and raw and isinstance(raw[0], dict) and "type" in raw[0]:
        rules_ordered = raw
    else:
#лазанья
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
        return round(current_balance, 2), history, fail_idx

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

#To core.py from dealer_input. Optimize and divide to modules
def full_list_save(username):
    """Сбор данных и моментальная запись в JSON пользователя"""
    name = input("Введите имя нового шаблона: ").strip()
    filename = f"{username}.json"

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except:
        data = {}

    if name in data:
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

#Запись данных  в json.
    # Заливаем в базу
    data[name] = [fixes, percs]
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"--- Шаблон '{name}' успешно сохранен ---")
# --------------------------------------------------------------