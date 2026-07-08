import json
from dataclasses import asdict
from decimal import Decimal
from domain import Template, Validator, Fix, Percentage


class NotFoundError(Exception):
    ...

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
                return {"templates": []}

            return json.loads(json_content)

    except (FileNotFoundError, json.JSONDecodeError):
        return {"templates": []}


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
        raise NotFoundError("Template didnt found")

    json_write(from_json)
    print("done")

def template_from_json(target_name):
    print("Reading files... ")
    templates_list = json_read().get('templates', list())

    target_template = None

    for template in templates_list:
        if template.get('name') == target_name:
            target_template = template
            break

    if target_template is None:
        raise NotFoundError(f"Ur asked {target_name} doesnt exist")

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


def json_list():
    templates_list = json_read().get('templates', list())

    if not templates_list:
        raise NotFoundError(f"Template or file doesnt exist")

    for exist_list in templates_list:
        print(f"- Шаблоны: {exist_list.get('name')}")