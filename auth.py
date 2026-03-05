#обязанности у этого модуля:
#To presentation.py
#Строго IO и веб интерфейс функционал

import json

def authenticate():
    print("\n=== ВХОД В СИСТЕМУ ===")
    user = input("Введите ваш логин: ").strip().lower()
    if not user: user = "guest"
    filename = f"{user}.json"

    try:
        # Пробуем открыть файл пользователя
        with open(filename, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"С возвращением, {user}!")
    except (FileNotFoundError, json.JSONDecodeError):
        # Если файла нет — создаем новый с базовой структурой
        choice = input(f"Профиль '{user}' не найден. Создать новый? (y/n): ").lower()
        if choice == 'y':
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({"piggybanks": {}}, f, indent=4)
            print(f"Создана личная база: {filename}")
        else:
            return None
    return user
