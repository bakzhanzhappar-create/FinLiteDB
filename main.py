from dealer import request, specify, goodbye, wrong_value, about_salary, about_calculate
from calculator import test, test2

def main():
    print("Hello User! What we can help you?")

    while True:
        command=request().lower()

        if "calculate" == command:
            test()
            test2()

        elif "remind" in command:
            defined = specify().lower()
            if "about salary" in defined:
                about_salary()

            elif "about calculate" in defined:
                about_calculate()

            else:
                wrong_value()

        elif "exit" in command:
            goodbye()
            break
        else:
            wrong_value()
if __name__ == '__main__':
    main()
