import json
from dataclasses import asdict
from decimal import Decimal
from core import Template, Validator, Fix, Percentage


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


def json_write(to_json):
    with open("user.json", 'w', encoding="utf-8") as user_file:
        json.dump(to_json, user_file, ensure_ascii=False, cls=DecimalEncoder)
        return True


def json_read():
    try:
        with open("user.json", 'r', encoding="utf-8") as user_file:
            json_content = user_file.read().strip()

            if not json_content:
                return {"templates": [], "banks": []}

            return json.loads(json_content)

    except (FileNotFoundError, json.JSONDecodeError):
        return {"templates": [], "banks": []}


def packing_to_json(test):
    print("Unpacking template")
    print("CONVERTING TO JSON... ")
    packed = asdict(test)

    is_template = hasattr(test, 'payments')
    from_json = json_read()

    if is_template:
        for packed_type, packed_data in zip(test.payments, packed['payments']):
            packed_data['__type__'] = type(packed_type).__name__

        correct_templates = list()

        for template in from_json['templates']:
            if template.get('name') != packed['name']:
                correct_templates.append(template)

        correct_templates.append(packed)
        from_json['templates'] = correct_templates

    else:
        correct_banks = list()

        for bank in from_json['banks']:
            if bank.get('name') != packed['name']:

                correct_banks.append(bank)
        correct_banks.append(packed)

        from_json['banks'] = correct_banks

    json_write(from_json)
    print("done")
    
def get_available_templates() -> list[str]:
    return [template_name for template in templates_list if (template_name := template.get("name")) is not None]

def packing_from_json(target_name):
    print("Reading files... ")
    from_json = json_read()

    templates_list = from_json.get('templates', list())

    if not templates_list:
        raise FileNotFoundError(f"File doesnt exist")

    # Показываем пользователю, какие шаблоны у нас вообще есть в базе
    print("\nДоступные шаблоны:")
    for exist_list in templates_list:
        print(f"- {exist_list.get('name')}")

    target_template = None

    for template in templates_list:
        if template.get('name') == target_name:
            target_template = template
            break

    if target_template is None:
        raise FileNotFoundError(f"Ur asked {target_template} doesnt exist")

    cleaned_payments = list()

    for payment_dict in target_template.get('payments', list()):

        raw_value = payment_dict['value']
        checked_value = Validator(value=raw_value, target_type=Decimal)
        decimal_value = checked_value.value

        class_type = payment_dict.pop('__type__', None)
        description = payment_dict['description']

        if class_type == 'Fix':
            obj = Fix(value=decimal_value, description=description)
        elif class_type == 'Percentage':
            obj = Percentage(value=decimal_value, description=description)
        else:
            obj = Fix(value=decimal_value, description=description)

        cleaned_payments.append(obj)

    return Template(name=target_template.get('name', 'Шаблон'), payments=cleaned_payments)
