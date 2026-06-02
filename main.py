from core import Template, Validator, Percentage, Fix
from decimal import Decimal


def works():
    print("works!")


def add_percentage():
    values: Decimal = (input("ввод суммы процента "))
    desc: str = input("Дайте описание ")
    test.payments.append(Percentage(Decimal(f'{values}'), description=desc))
    return True


def add_fix():
    values: Decimal = (input("ввод суммы фиксированного "))
    desc: str = input("Дайте описание ")
    test.payments.append(Fix(Decimal(f'{values}'), description=desc))
    return True

def ask_amount():
    amount: Decimal = input("Введите сумму для обработки ")
    check_amount=Validator(amount)
    amount=test.apply(amount)

while True:
    testing = str(input("ввод: "))
    if testing=="add template ":
        works()
        test=Template()

    if testing=="add percentage ":
        works()
        add_percentage()

    if testing=="add fix ":
        works()
        add_fix()

    if testing=="show template ":
        works()
        print(test)

    if testing=="execute template ":
        works()
        ask_amount()
        test.apply()
    if testing=="exit":
        works()
        break