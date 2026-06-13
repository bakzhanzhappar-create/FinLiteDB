import json
from dataclasses import asdict
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

def save_to_json(to_user_file):
    with open("baga.json", mode='w', encoding="utf-8") as user_file:
        json.dump(to_user_file, user_file, ensure_ascii=False, indent=4, cls=DecimalEncoder)
        return True

def packing_template(test):
    print("Unpacking template")
    packed_template=asdict(test)
    print(f"CONVERTING TO JSON  {packed_template}")
    save_to_json(packed_template)
    print("done")


def packing_bank(bank_test):
    print("Unpacking bank")
    packed_bank=asdict(bank_test)
    print(f"CONVERTING TO JSON {packed_bank}")
    save_to_json(packed_bank)
    print("done")