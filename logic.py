from decimal import Decimal
from core import Fix, Percentage, Template
from storage import StorageManager


def calculate_finance(amount: float, rules_raw: list, name: str) -> dict:
    d_amount = Decimal(str(amount))
    payments = []

    for r in rules_raw:
        val = Decimal(str(r['val']))
        if r['type'] == 'f':
            payments.append(Fix(val, r['desc']))
        else:
            payments.append(Percentage(val, r['desc']))

    tpl = Template(name=name, payments=payments)
    remainder, history, fail_idx, total_deducted = tpl.run(d_amount)

    return {
        "remainder": float(remainder),
        "deducted": float(total_deducted),
        "history": history,
        "fail_idx": fail_idx,
        "percent": float((total_deducted / d_amount * 100) if d_amount else 0),
    }


def execute_fifo(username: str, amount: float, template_name: str):
    """
    FIX: replaced db.get_data() → db.load_user_data() (correct method name),
         added ['templates'] key access,
         replaced db.log_calculation() → db.add_history() (correct method name).
    """
    db = StorageManager(username)
    data = db.load_user_data()
    raw_rules = data.get('templates', {}).get(template_name, [])

    payments = []
    for r in raw_rules:
        val = Decimal(str(r.get('val', 0)))
        desc = r.get('desc', 'пусто')
        if r.get('type') == 'f':
            payments.append(Fix(val, desc))
        else:
            payments.append(Percentage(val, desc))

    template = Template(name=template_name, payments=payments)
    d_amount = Decimal(str(amount))
    remainder, history, fail_idx, total_deducted = template.run(d_amount)

    db.add_history({
        "template": template_name,
        "input": amount,
        "remainder": float(remainder),
        "deducted": float(total_deducted),
    })

    return float(remainder), history, fail_idx, float(total_deducted)
