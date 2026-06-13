import json
from dataclasses import asdict

def save_to_json(to_user_file):
    with open("baga.json", mode='w', encoding="utf-8") as user_file:
        json.dump(to_user_file, user_file, ensure_ascii=False, indent=4)
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


# ввод: auto template
# works!
# ввод: save template to json
# Unpacking template
# CONVERTING TO JSON  {'payments': [{'value': Decimal('10000'), 'description': 'coca cola'}, {'value': Decimal('20000'), 'description': 'Пусто'}, {'value': Decimal('1000'), 'description': 'Пусто'}, {'value': Decimal('30'), 'description': 'Пусто'}], 'name': 'Шаблон'}
# Traceback (most recent call last):
#   File "C:\Users\baga\PycharmProjects\FinLiteDB\main.py", line 95, in <module>
#     packing_template(test)
#     ~~~~~~~~~~~~~~~~^^^^^^
#   File "C:\Users\baga\PycharmProjects\FinLiteDB\storage.py", line 13, in packing_template
#     save_to_json(packed_template)
#     ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
#   File "C:\Users\baga\PycharmProjects\FinLiteDB\storage.py", line 6, in save_to_json
#     json.dump(to_user_file, user_file, ensure_ascii=False, indent=4)
#     ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\baga\AppData\Local\Programs\Python\Python314\Lib\json\__init__.py", line 179, in dump
#     for chunk in iterable:
#                  ^^^^^^^^
#   File "C:\Users\baga\AppData\Local\Programs\Python\Python314\Lib\json\encoder.py", line 442, in _iterencode
#     yield from _iterencode_dict(o, _current_indent_level)
#   File "C:\Users\baga\AppData\Local\Programs\Python\Python314\Lib\json\encoder.py", line 411, in _iterencode_dict
#     yield from chunks
#   File "C:\Users\baga\AppData\Local\Programs\Python\Python314\Lib\json\encoder.py", line 324, in _iterencode_list
#     yield from chunks
#   File "C:\Users\baga\AppData\Local\Programs\Python\Python314\Lib\json\encoder.py", line 411, in _iterencode_dict
#     yield from chunks
#   File "C:\Users\baga\AppData\Local\Programs\Python\Python314\Lib\json\encoder.py", line 449, in _iterencode
#     newobj = _default(o)
#   File "C:\Users\baga\AppData\Local\Programs\Python\Python314\Lib\json\encoder.py", line 180, in default
#     raise TypeError(f'Object of type {o.__class__.__name__} '
#                     f'is not JSON serializable')
# TypeError: Object of type Decimal is not JSON serializable
# when serializing dict item 'value'
# when serializing list item 0
# when serializing dict item 'payments'
#
# Process finished with exit code 1
