from dealer import message_positive
import json

#JSON append
def json_append():
        try:
            try:
                with open("template_storage.json", 'r', encoding='utf-8') as f:
                    full_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                full_data = {}

            full_data.update(template_dict)

            with open("template_storage.json", 'w', encoding='utf-8') as f:
                json.dump(full_data, f, indent=4, ensure_ascii=False)
            message_positive()
        except Exception as e:
            print(f"Error saving: {e}")