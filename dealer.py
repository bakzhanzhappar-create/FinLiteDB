def request():
    command= str(input("\n Type your command: <calculate> to calculate you somethings, <remind> to remind instructions, <exit> to exit :) "))
    return command


def wrong_value():
    print("I think you made some mistake with type of input")


def specify():
    try:
        specify_input: str=str(input(f"What exactly you want to know about?? In current moment we have information for <about salary>, <about calculate> "))
        return specify_input
    except ValueError:
        wrong_value()
        return False

def Goodbye():
    print("\nGoodbye! :)")

def not_enough_value():
    print("Sorry, you don't have enough money")
    print("\n BROKE NIGGA ALERT"*5)

def about_salary():
    print("\nIn current moment <for salary> is meant to calculate your input under specified rules: Just taking from inputs 7%")

def about_calculate():
    print("\n Балду гоняю")
    print("\n Схитрил систему")


#Крч, внутри дилера надо добавить класс чтобы все комментарии на режимы можно отделить от оповещений

# калькуляторе надо разобраться с вычислениями и его вывода

#Нужно редактировать название, соответственно покопаться в гите

#Надо привыкнуть к использованию Обсидиана