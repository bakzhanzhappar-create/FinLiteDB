# import json
from dataclasses import asdict
# def save_to_json(to_user_file):
#     with open("user_file.json", mode='w', encoding="utf-8") as user_file:
#         json.dump(to_user_file, user_file, ensure_ascii=False, indent=4)
#         return True

def unpack_template(test):
    print("Unpacking template")
    print(asdict(test))
    print(type(test))

def unpack_bank(bank_test):
    print("Unpacking bank")
    print(asdict(bank_test))
    print(type(bank_test))

# ввод: add template
# works!
# ввод: add fix
# ввод: 120
# ввод: add fix
# ввод суммы фиксированного 120
# Дайте описание nigga
# works!
# ввод: save template to json
# ввод: save template to json
# Traceback (most recent call last):
#   File "C:\Users\baga\PycharmProjects\FinLiteDB\main.py", line 77, in <module>
#     save_to_json(test)
#     ~~~~~~~~~~~~^^^^^^
#   File "C:\Users\baga\PycharmProjects\FinLiteDB\storage.py", line 5, in save_to_json
#     json.dump(to_user_file, user_file, ensure_ascii=False, indent=4)
#     ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "C:\Users\baga\AppData\Local\Programs\Python\Python314\Lib\json\__init__.py", line 179, in dump
#     for chunk in iterable:
#                  ^^^^^^^^
#   File "C:\Users\baga\AppData\Local\Programs\Python\Python314\Lib\json\encoder.py", line 449, in _iterencode
#     newobj = _default(o)
#   File "C:\Users\baga\AppData\Local\Programs\Python\Python314\Lib\json\encoder.py", line 180, in default
#     raise TypeError(f'Object of type {o.__class__.__name__} '
#                     f'is not JSON serializable')
# TypeError: Object of type Template is not JSON serializable
#
# Process finished with exit code 1