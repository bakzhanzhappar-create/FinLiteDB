from dealer import wrong_value

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
