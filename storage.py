import json
from dataclasses import asdict
from decimal import Decimal
from core import Template, Validator, Fix, Percentage

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

#запись и чтение с нуля переделай


def packing_to_json(test):
    print("Unpacking template")
    packed=asdict(test)

    for packed_type, packed_data in zip(test.payments, packed['payments']):
        packed_data['__type__'] = type(packed_type).__name__

    print("CONVERTING TO JSON... ")
    check_write(packed)
    print("done")


def packing_from_json():
    print("Reading files... ")
    from_json=check_read()
    if not from_json:
        print("ERROR...")
        return Template()

    cleaned_payments=list()

    for payment_dict in from_json.get('payments', list()):

        raw_value=payment_dict('value')
        checked_value=Validator(value=raw_value, target_type=Decimal)
        decimal_value=checked_value.value

        class_type=payment_dict.pop('__type__', None)
        description=payment_dict('description')

        if class_type == 'Fix':
            obj = Fix(value=decimal_value, description=description)
        elif class_type == 'Percentage':
            obj = Percentage(value=decimal_value, description=description)
        else:
            # Фолбэк на случай, если маркер почему-то не записался
            obj = Fix(value=decimal_value, description=description)

        cleaned_payments.append(obj)
    return Template(name=from_json.get('name', 'Шаблон'), payments=cleaned_payments)
