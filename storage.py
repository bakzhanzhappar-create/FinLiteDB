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

    def create_goal(self):
        name = input("На что копим? (имя цели): ").strip()
        target = float(input("Целевая сумма: "))
        link = input("Ссылка на товар/описание: ")

        data = self._read()
        if "piggybanks" not in data: data["piggybanks"] = {}

        data["piggybanks"][name] = {
            "target": target,
            "current": 0.0,
            "link": link
        }
        self._write(data)
        print(f"Копилка '{name}' активирована!")

    def deposit(self, amount):
        data = self._read()
        banks = data.get("piggybanks", {})

        if not banks:
            print("У вас нет активных копилок.")
            return

        print("Ваши цели:", list(banks.keys()))
        choice = input("В какую копилку закинуть остаток?: ")

        if choice in banks:
            banks[choice]["current"] += amount
            self._write(data)
            prog = (banks[choice]['current'] / banks[choice]['target']) * 100
            print(f"Зачислили {amount}. Прогресс '{choice}': {round(prog, 1)}%")
        else:
            print("Копилка не найдена.")
