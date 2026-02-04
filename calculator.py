from dealer import wrong_value, not_enough_value

def calculate():
    try:
        a=int(input("\n Type number for a: "))
        b=int(input("\n Type number for b: "))
        s=a+b
        print(f"Sum of a and b is {s}")
    except ValueError:
        wrong_value()
        return False

def for_salary():
    try:
        salary_input=int(input("\n Type number for salary: "))
        percent_for_salary=0.7
        sum_salary=salary_input*percent_for_salary
        print(f"\n Sum of salary is {sum_salary}")
    except ValueError:
        wrong_value()
        return False

def test():
    try:
        salary = int(input("\nType value of your salary: "))

        for_deposit = salary * 0.15
        for_road = 4950
        for_japan_trip = 500
        for_myself = salary - for_deposit - for_road - for_japan_trip

        print(
            f"\nSum of deposit is {for_deposit}"
            f"\nSum of road is {for_road}"
            f"\nSum of japan trip is {for_japan_trip}"
            f"\nSum of myself is {for_myself}"
        )

        if for_myself < 0:
            not_enough_value()

    except ValueError:
        wrong_value()

def test2():
    try:
        stipendya = int(input("\nType value of your salary: "))

        for_deposit = stipendya * 0.15
        tax = stipendya * 0.07
        tax_for_niggas = stipendya * 0.02
        for_myself = stipendya - for_deposit - tax - tax_for_niggas
        print(
            f"\nSum of deposit is {stipendya}"
            f"\nSum of tax is {tax}"
            f"\nSum of second tax is {tax_for_niggas}"
            f"\nSum of myself is {for_myself}"
        )

        if for_myself < 0:
            not_enough_value()
    except ValueError:
        wrong_value()
        #прочти статью про JSON из заметки Obsidian