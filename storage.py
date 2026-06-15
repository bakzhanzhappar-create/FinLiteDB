import json
from dataclasses import asdict
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

def check_write(to_user_file):
    read()
    if read == True:
        append_json(to_user_file)
    else:
        write_json(to_user_file)


def check_read():
    read()
    if read == True:
        read_json()
        return read_json
    else:
        return False


def append_json(to_user_file):
    with open("user.json", mode='a', encoding="utf-8") as user_file:
        json.dump(to_user_file, user_file, ensure_ascii=False, indent=4, cls=DecimalEncoder)
        return True


def write_json(to_user_file):
    with open("user.json", mode='w', encoding="utf-8") as user_file:
        json.dump(to_user_file, user_file, ensure_ascii=False, indent=4, cls=DecimalEncoder)
        return True


def read():
    try:
        with open("user.json", mode='r', encoding="utf-8"):
            return True
    except FileNotFoundError("The user file is missing or we cant find it"):
        return False


def read_json():
    with open("user.json", mode='r', encoding="utf-8") as user_file:
        from_file=json.load(user_file)
        return from_file


def packing_to_json(data):
    print("Unpacking template")
    packed=asdict(data)
    print("CONVERTING TO JSON ...")
    check_write(packed)
    print("done")


def packing_from_json(data):
    print("Reading files... ")
    from_json=check_read()
    return from_json