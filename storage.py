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

# import json
# from dataclasses import dataclass
# from dealer_input import template_name_variable, message_negative
# JSON append
# def json_append():
#     try:
#         try:
#             with open("template_storage.json", 'r', encoding='utf-8') as f:
#                 full_data = json.load(f)
#         except (FileNotFoundError, json.JSONDecodeError):
#             full_data = {}
#
#         full_data.update(template_dict)
#
#         with open("template_storage.json", 'w', encoding='utf-8') as f:
#             json.dump(full_data, f, indent=4, ensure_ascii=False)
#         message_positive()
#     except Exception as e:
#         print(f"Error saving: {e}")
#
#
# # JSON reader
# def json_reader():
#     try:
#         with open("template_storage.json", 'r', encoding='utf-8') as f:
#             template_dict = json.load(f)
#             print(template_dict)
#
#     except FileNotFoundError:
#         print("Storage doesn't exist yet")
#
# @dataclass
# class JSONappend:
#     def json_write(self):
#         try:
#             with open(f"{template_name_variable}.json", mode='w', encoding='utf-8') as file_append:
#                 full_data = json.load(file_append)
#         except FileNotFoundError:
#             message_negative()
#         return full_data
#
# @dataclass
# class JSONreader:
#     def json_exist_check(self):
#         try:
#             with open(f"{template_name_variable}.json", mode='r', encoding='utf-8') as file_exist:
#                 full_data=json.load(file_exist)
#         except (FileNotFoundError, json.JSONDecodeError):
#             full_data = {}
#             message_negative()
#
#     def json_read(self):
#         try:
#             with open(f"{template_name_variable}.json", mode='r', encoding='utf-8') as file_read:
#                 full_data = json.load(file_read)
#         except FileNotFoundError:
#             full_data = {}
#             message_negative()
#         return full_data