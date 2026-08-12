from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

class InvalidTypeError(Exception):
    ...

class InvalidTemplateError(Exception):
    ...

class InvalidPaymentError(Exception):
    ...


@dataclass(frozen=True, slots=True)
class Payment:
    value: Decimal=Decimal('0')
    description: str = field(default="Пусто")

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidPaymentError("Value must be positive")


@dataclass(frozen=True, slots=True)
class Percentage(Payment):

    def __post_init__(self) -> None:
        if self.value < 0:
            raise InvalidPaymentError("Value must be positive")

        if self.value > 100:
            raise InvalidPaymentError("Value must be less than 100")

    def apply(self, value: Decimal) -> Decimal:
        result=value - (self.value * value) / Decimal('100')
        return result.quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)


@dataclass(frozen=True, slots=True)
class Fix(Payment):

    def apply(self, amount: Decimal) -> Decimal:
        return amount - self.value


@dataclass(slots=True)
class Validator:
    value: str | Decimal
    target_type: type = Decimal

    def __post_init__(self) -> Decimal:
        try:
            correct_value=self.value=self.target_type(self.value)
            return correct_value
        except TypeError:
            raise InvalidTypeError(f" {self.value} тут есть некорректный символ")


@dataclass(frozen=True, slots=True)
class Template:

    name: str = field(default="Шаблон")
    payments: list[Fix | Percentage] = field(default_factory=list)

    def apply(self, amount: Decimal) -> Decimal:
        for payment in self.payments:
            amount = payment.apply(amount)
        return amount


    def partially_delete(self, index) -> list:
        if self.payments[index] in self.payments:
            del self.payments[index]
        return self.payments


@dataclass(slots=True)
class APIValidator(Validator):

    def to_template(self) -> Template:
        try:
            name = str(self.value.get("name", "Шаблон"))
            raw_payments = self.value.get("payments", [])

            cleaned_payments = []
            for percentage in raw_payments:
                p_type = str(percentage.get("type")).lower()
                val = Decimal(str(percentage.get("value", 0)))
                desc = str(percentage.get("description", "Пусто"))

                if "percent" in p_type:
                    cleaned_payments.append(Percentage(value=val, description=desc))
                else:
                    cleaned_payments.append(Fix(value=val, description=desc))

            return Template(name=name, payments=cleaned_payments)
        except (TypeError, ValueError):
            raise InvalidTypeError(f"Ошибка валидации шаблона:")


#С этим чето надо делать
def execute_budget_simulation(template: Template, initial_amount: Decimal) -> dict:
    current_balance = initial_amount
    success = True
    error_step = None
    history = []

    for idx, payment in enumerate(template.payments, start=1):
        if current_balance == Decimal('0'):
            success = False
            error_step = idx
            history.append({
                "step": idx,
                "description": payment.description,
                "type": "percentage" if isinstance(payment, Percentage) else "fix",
                "display_deducted": f"{payment.value}% (0 ₸)" if isinstance(payment,
                                                                            Percentage) else f"{payment.value} ₸",
                "deducted_amount": 0.0,
                "balance_after": 0.0,
                "status": "zero_balance_stop"
            })
            break

        if isinstance(payment, Fix):
            deducted = payment.value
            balance_after = current_balance - deducted

            # Сценарий #2: не хватило частично на этом шаге (ушли в минус)
            if current_balance < payment.value:
                success = False
                error_step = idx
                history.append({
                    "step": idx,
                    "description": payment.description,
                    "type": "fix",
                    "display_deducted": f"{deducted} ₸",
                    "deducted_amount": float(deducted),
                    "balance_after": float(balance_after),
                    "status": "insufficient_funds"
                })
                break

            current_balance = balance_after
            history.append({
                "step": idx,
                "description": payment.description,
                "type": "fix",
                "display_deducted": f"{deducted} ₸",
                "deducted_amount": float(deducted),
                "balance_after": float(current_balance),
                "status": "ok"
            })

        elif isinstance(payment, Percentage):
            balance_after = payment.apply(current_balance)
            deducted = current_balance - balance_after

            # В скобках выводим конкретную сумму от введенного остатка
            display_str = f"{payment.value}% ({float(deducted):,.2f} ₸)"

            current_balance = balance_after
            history.append({
                "step": idx,
                "description": payment.description,
                "type": "percentage",
                "display_deducted": display_str,
                "deducted_amount": float(deducted),
                "balance_after": float(current_balance),
                "status": "ok"
            })

    return {
        "template_name": template.name,
        "initial_amount": float(initial_amount),
        "final_balance": float(current_balance),
        "success": success,
        "error_step": error_step,
        "history": history
    }

scholarship= Decimal('52367')
t=Template(
    payments=[
        Fix(Decimal('1320'), description="за проезд"),
        Fix(Decimal('5790'), description="за тариф"),
        Fix(Decimal('5000'), description="сестренке"),
        Fix(Decimal('28000'), description="на все про все"),
        Fix(Decimal('12262'), description="самоналог"),
    ])
print(t.payments)
t.partially_delete(1)
print(t.payments)