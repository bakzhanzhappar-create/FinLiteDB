from dealer import request, specify, Goodbye, wrong_value, about_salary, about_calculate
from calculator import calculate, test

def main():
    print("Hello User! What we can help you?")

    while True:
        command=request().lower()

        if "calculate" == command:
            test()
            # calculate()

        elif "remind" in command:
            defined = specify().lower()
            if "about salary" in defined:
                about_salary()

            elif "about calculate" in defined:
                about_calculate()

            else:
                wrong_value()

        elif "exit" in command:
            Goodbye()
            break
        else:
            wrong_value()
if __name__ == '__main__':
    main()
