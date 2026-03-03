#обязанности у этого модуля:
#Чтение и запись json-а

import json


class PiggyBank:
    def __init__(self, username):
        self.filename = f"{username}.json"

    def _read(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"piggybanks": {}}

    def _write(self, data):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def create_goal(self, name=None, target=None, link=None):
        if name is None:
            name = input("На что копим? (имя цели): ").strip()
        if target is None:
            target = float(input("Целевая сумма: "))
        if link is None:
            link = input("Ссылка на товар/описание: ")

        data = self._read()
        if "piggybanks" not in data:
            data["piggybanks"] = {}

        data["piggybanks"][name] = {
            "target": float(target),
            "current": 0.0,
            "link": link or ""
        }
        self._write(data)
        if name is not None and target is not None:
            return
        print(f"Копилка '{name}' активирована!")

    def deposit(self, amount, goal_name=None):
        data = self._read()
        banks = data.get("piggybanks", {})

        if not banks:
            if goal_name is not None:
                return False
            print("У вас нет активных копилок.")
            return

        if goal_name is not None:
            choice = goal_name
        else:
            print("Ваши цели:", list(banks.keys()))
            choice = input("В какую копилку закинуть остаток?: ")

        if choice in banks:
            banks[choice]["current"] += float(amount)
            self._write(data)
            if goal_name is None:
                prog = (banks[choice]['current'] / banks[choice]['target']) * 100
                print(f"Зачислили {amount}. Прогресс '{choice}': {round(prog, 1)}%")
            return True
        return False
