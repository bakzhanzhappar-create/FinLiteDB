from core import Template, Validator, Percentage, Fix, Bank
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

def fulfill_bank():
    bank_test.name= str(input("Введите название для банка: "))
    bank_test.target_scale=ask_amount()
    bank_test.description= str(input("Что вы хотите записать по поводу этого банка?: "))

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

    if testing == "add bank ":
        works()
        bank_test = Bank()

    if testing == "show bank ":
        works()
        print(bank_test)

    if testing == "fulfill bank ":
        works()
        fulfill_bank()

    if testing == "money to bank ":
        bank_test.add_money(ask_amount())
        if bank_test.is_target_success() == True:
            print("we have enough money")
        else:
            print(f"U nigga close to the target there left {bank_test.target_scale - bank_test.amount} to the target for {bank_test.description}!")
        works()

    if testing=="exit":
        works()
        break