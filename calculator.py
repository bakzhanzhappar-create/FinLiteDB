def calculate():
    try:
        a=int(input("\n Type number for a: "))
        b=int(input("\n Type number for b: "))
        s=a+b
        print(f"Sum of a and b is {s}")
    except ValueError:
        print("I think you made some mistake with type of number")
        return False

def for_salary():
    try:
