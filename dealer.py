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