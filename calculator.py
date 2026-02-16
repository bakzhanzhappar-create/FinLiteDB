from dealer import wrong_value, not_enough_value

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



# формула для процентных правил 4650=5000-(5000*7/100), если надо отнять 7% из 5000
# формула для процентных правил 4650=5000-(5000*7/100), если надо отнять 7% из 5000