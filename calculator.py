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

# def test():
#     try:
#         test1=int(input("\n Type value of your salary: "))
#         for_deposit=test1*0.15
#         for_road=test1-for_deposit
#         for_japan_trip=for_road-500
#         for_myself=for_japan_trip
#         if for_deposit <= 0 or for_road <= 0 or for_japan_trip <= 0 or for_myself <= 0:
#             not_enough_value()
#         else:
#             print(f"\n Sum of deposit is {for_deposit}\n Sum of road is {for_road} \n Sum of myself is {for_myself}\n Sum of japan trip is {for_japan_trip}")
#     except ValueError:
#         wrong_value()
#         return False

def test():
    try:
        salary = int(input("\nType value of your salary: "))

        for_deposit = salary * 0.15
        for_road = salary - for_deposit
        for_japan_trip = for_road - 500
        for_myself = for_japan_trip

        print(f"\n Sum of deposit is {for_deposit}\n Sum of road is {for_road} \n Sum of myself is {for_myself}\n Sum of japan trip is {for_japan_trip}")

        if any(value < 0 for value in [
            for_deposit,
            for_road,
            for_japan_trip,
            for_myself
        ]):
            not_enough_value()

    except ValueError:
        wrong_value()


