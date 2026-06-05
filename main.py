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
    value: str = input("Введите сумму для обработки ")
    checked=Validator(value)
    return checked.value

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
        use_amount=ask_amount()
        result=test.apply(use_amount)
        print(result)
    if testing=="exit":
        works()
        break
# C:\Users\baga\AppData\Local\Programs\Python\Python314\python.exe C:\Users\baga\PycharmProjects\FinLiteDB\main.py
# ввод: add template
# works!
# ввод: add fix
# works!
# ввод суммы фиксированного 1200
# Дайте описание nigga
# ввод: execute template
# works!
# Введите сумму для обработки 54200
# Traceback (most recent call last):
#   File "C:\Users\baga\PycharmProjects\FinLiteDB\main.py", line 47, in <module>
#     ask_amount()
#     ~~~~~~~~~~^^
#   File "C:\Users\baga\PycharmProjects\FinLiteDB\main.py", line 25, in ask_amount
#     value=test.apply(value)
#   File "C:\Users\baga\PycharmProjects\FinLiteDB\core.py", line 100, in apply
#     amount = payment.apply(amount)
#   File "C:\Users\baga\PycharmProjects\FinLiteDB\core.py", line 43, in apply
#     return amount - self.value
#            ~~~~~~~^~~~~~~~~~~~
# TypeError: unsupported operand type(s) for -: 'str' and 'decimal.Decimal'
#
# Process finished with exit code 1