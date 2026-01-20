from dealer import request
from calculator import calculate


def main():
    print("Hello User!")

    while True:
        command=request()
        command_lowered=command.lower()

        if "calculate" in command_lowered:
            calculate()

        elif "exit" in command_lowered:
            print("Goodbye!!")
            break

if __name__ == '__main__':
    main()
