from core import Template, Validator, Percentage, Fix, Bank
from decimal import Decimal
from storage import packing_template, packing_bank

def works():
    print("works!")

def auto_template():
    test=Template(
        payments=[
        Fix(Decimal('10000'), "coca cola"),
        Fix(Decimal('20000')),
        Fix(Decimal('1000')),
        Percentage(value=Decimal('30'))])
    works()
    return test

def auto_bank():
    bank_test=Bank(
        name="Lada",
        target_scale=Decimal('45000'),
        description="Once i have a dream that one day ill move w niggas to diff cities")
    works()
    return bank_test


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
        test=Template()
        works()

    if testing=="add percentage ":
        add_percentage()
        works()

    if testing=="add fix ":
        add_fix()
        works()

    if testing=="show template ":
        print(test)
        works()

    if testing=="execute template ":
        use_amount=ask_amount()
        result=test.apply(use_amount)
        works()
        print(result)

    if testing == "add bank ":
        bank_test = Bank()
        works()

    if testing == "show bank ":
        print(bank_test)
        works()

    if testing == "fulfill bank ":
        fulfill_bank()
        works()

    if testing == "money to bank ":
        bank_test.add_money(ask_amount())
        if bank_test.is_target_success() == True:
            print("we have enough money")
        else:
            print(f"U nigga close to the target there left {bank_test.target_scale - bank_test.amount} to the target for {bank_test.description}!")
        works()

    if testing == "save template to json":
        packing_to_json(test)

    if testing == "save bank to json":
        packing_to_json(bank_test)

    if testing=="auto template":
        test=auto_template()

    if testing=="auto bank":
        bank_test=auto_bank()

    if testing=="exit":
        works()
        break