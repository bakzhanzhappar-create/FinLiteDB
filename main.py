from dealer import request
from calculator import calculate
from reminder import

def main():
    print("Hello User! What we can help you?")

    while True:
        command=request()
        command_lowered=command.lower()

        if "calculate" in command_lowered:
            calculate()

        elif "exit" in command_lowered:
            print("Goodbye!!")
            break
        elif "reminder" in command_lowered:


if __name__ == '__main__':
    main()
