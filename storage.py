import json
from dataclasses import asdict
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


def check_write(to_user_file):
    if read() == True:
        append_json(to_user_file)
    else:
        write_json(to_user_file)


def check_read():
    if read() == True:
        return read_json()
    else:
        return False


def append_json(to_user_file):
    with open("user.json", mode='a', encoding="utf-8") as user_file:
        user_file.write("\n")
        json.dump(to_user_file, user_file, ensure_ascii=False, indent=4, cls=DecimalEncoder)
        return True


def write_json(to_user_file):
    with open("user.json", mode='w', encoding="utf-8") as user_file:
        json.dump(to_user_file, user_file, ensure_ascii=False, indent=4, cls=DecimalEncoder)
        return True


def read_json():
    with open("user.json", mode='r', encoding="utf-8") as user_file:
        from_file=json.load(user_file)
        return from_file


def read():
    try:
        with open("user.json", mode='r', encoding="utf-8"):
            return True
    except FileNotFoundError:
        return False


def packing_to_json(test):
    print("Unpacking template")
    packed=asdict(test)
    print("CONVERTING TO JSON... ")
    check_write(packed)
    print("done")


def packing_from_json():
    print("Reading files... ")
    from_json=check_read()
    return from_json

#Допилить чтение из json
#Исправить момент чтобы знал где фикс а где процентное      не говоря про шаблоны и если их несколько с одним названием
#Как то продумать момент с взаимодействием нескольких объектов класса не под консоль а универсально
#С богом бля   Template(name={'name': 'Шаблон', 'payments': [{'value': '10000', 'description': 'coca cola'}, {'value': '20000', 'description': 'Пусто'}, {'value': '1000', 'description': 'Пусто'}, {'value': '30', 'description': 'Пусто'}]}, payments=[])
# если приглядется читает и инициализирует криво в name ВСЕ ТАМ ВАЛЯЕТСЯ, а в payments только уверенность