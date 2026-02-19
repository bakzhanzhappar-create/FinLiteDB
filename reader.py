import json
#JSON reader
def json_reader():
        try:
            with open("template_storage.json", 'r', encoding='utf-8') as f:
                template_dict = json.load(f)
                print(template_dict)

        except FileNotFoundError:
            print("Storage doesn't exist yet")