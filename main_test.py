#обязанности у этого модуля:
#Его роль это вызыв модулей исходя из значений условий

import core, presentation, storage_test
import auth, logic, storage, reader, dealer_input as di

def start_session():
    user = auth.authenticate()
    if not user: return False

    bank = storage.PiggyBank(user)

    while True:
        action = di.hello()

        if "add" in action:
            di.full_list_save(user)

        if "bank" in action:
            bank.create_goal()

        if "read" in action:
            reader.show_database(user)
            # Вывод копилок
            data = bank._read()
            if "piggybanks" in data and data["piggybanks"]:
#presentation.py
                print("\n ВАШИ КОПИЛКИ:")
                for n, i in data["piggybanks"].items():
                    prog = (i['current'] / i['target']) * 100
                    print(f"[{n}] {i['current']}/{i['target']} ({round(prog, 1)}%) | {i['link']}")
#--------------------------------------------------------------
        if "interact" in action:
            try:
#core.py
                sum_val = float(input("\nВведите сумму дохода: "))
                remains = logic.run_fifo(sum_val, user)
                if remains > 0:
                    if input("Закинуть остаток в копилку? (y/n): ").lower() == 'y':
                        bank.deposit(remains)
            except ValueError:
                print("Введите число!")
# --------------------------------------------------------------

        if "exit" in action:
            print(f"Сессия {user} закрыта.")
            break
    return True

if __name__ == "__main__":
    while True:
        if not start_session(): break
        if input("\nСменить пользователя? (y/n): ").lower() != 'y': break
