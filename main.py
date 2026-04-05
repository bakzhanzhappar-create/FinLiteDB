from reader import json_reader
from append import json_append
from dealer import hello

# storage
template_name_variable=list()
fix_number_list=list()
fix_description_list=list()
percent_number_list=list()
percent_description_list=list()


# main
while True:
    deal=hello().lower()
    if "add" in deal:
        full_list_append()

        print(template_name_variable)
        print(fix_number_list)
        print(fix_description_list)
        print(percent_number_list)
        print(percent_description_list)
        print("\n")

#converter
    if "convert" in deal:

        while len(fix_number_list) < len(template_name_variable):
            fix_number_list.append(0)
            fix_description_list.append("no fix")
        while len(percent_number_list) < len(template_name_variable):
            percent_number_list.append(0)
            percent_description_list.append("no percent")

        fix_full_list = list(zip(fix_number_list, fix_description_list))
        percent_full_list = list(zip(percent_number_list, percent_description_list))
        full_list = list(zip(fix_full_list, percent_full_list))
        template_dict = dict(zip(template_name_variable, full_list))


        template_name_variable.clear()
        fix_number_list.clear()
        fix_description_list.clear()
        percent_number_list.clear()
        percent_description_list.clear()

#JSON append
        json_append()
#JSON read
    if "read" in deal:
        json_reader()
    if "interact" in deal:
        amount = int(input("Enter amount for the template: "))
        print(f"{calculate(amount)}")

    if "exit" in deal:
        break


# формула для процентных правил 5000-(5000*7/100)=4650, если надо отнять 7% из 5000
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
                print("\n ВАШИ КОПИЛКИ:")
                for n, i in data["piggybanks"].items():
                    prog = (i['current'] / i['target']) * 100
                    print(f"[{n}] {i['current']}/{i['target']} ({round(prog, 1)}%) | {i['link']}")

        if "interact" in action:
            try:
                sum_val = float(input("\nВведите сумму дохода: "))
                remains = logic.run_fifo(sum_val, user)
                if remains > 0:
                    if input("Закинуть остаток в копилку? (y/n): ").lower() == 'y':
                        bank.deposit(remains)
            except ValueError:
                print("Введите число!")

        if "exit" in action:
            print(f"Сессия {user} закрыта.")
            break
    return True

if __name__ == "__main__":
    while True:
        if not start_session(): break
        if input("\nСменить пользователя? (y/n): ").lower() != 'y': break


from reader import json_reader
from append import json_append
from dealer_input import hello

# storage
template_name_variable=list()
fix_number_list=list()
fix_description_list=list()
percent_number_list=list()
percent_description_list=list()


# main
while True:
    deal=hello().lower()
    if "add" in deal:
        full_list_append()

        print(template_name_variable)
        print(fix_number_list)
        print(fix_description_list)
        print(percent_number_list)
        print(percent_description_list)
        print("\n")

#converter
    if "convert" in deal:

        while len(fix_number_list) < len(template_name_variable):
            fix_number_list.append(0)
            fix_description_list.append("no fix")
        while len(percent_number_list) < len(template_name_variable):
            percent_number_list.append(0)
            percent_description_list.append("no percent")

        fix_full_list = list(zip(fix_number_list, fix_description_list))
        percent_full_list = list(zip(percent_number_list, percent_description_list))
        full_list = list(zip(fix_full_list, percent_full_list))
        template_dict = dict(zip(template_name_variable, full_list))


        template_name_variable.clear()
        fix_number_list.clear()
        fix_description_list.clear()
        percent_number_list.clear()
        percent_description_list.clear()

#JSON append
        json_append()
#JSON read
    if "read" in deal:
        json_reader()
    if "interact" in deal:
        amount = int(input("Enter amount for the template: "))
        print(f"{calculate(amount)}")

    if "exit" in deal:
        break


# формула для процентных правил 5000-(5000*7/100)=4650, если надо отнять 7% из 5000



from dataclasses import dataclass
class Person:
    def __init__(self, name, age, gender):
        self.name=name
        self.age=age
        self.gender=gender
        print("Person created")

@dataclass
class Person:
    name: str
    age: int
    gender: str
    print("Person created!")

name=str(input("Enter your name: "))
age=int(input("Enter your age: "))
gender=str(input("Enter your gender: "))
person=Person(name,age,gender)
print(f"We added new contact! Welcome {person.name} ur info is {person.age} years old and {person.gender}")

with open(f"{name}.txt", mode='w', encoding="utf-8") as file:
    file.write(f"Hello {person.name}!")
    print("\nSuccessfully saved!")