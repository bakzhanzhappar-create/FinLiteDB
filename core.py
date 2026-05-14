from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP


class InvalidPaymentError(Exception):
    pass


def money_round(value: Decimal) -> Decimal:
    return value.quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)


@dataclass(frozen=True, slots=True)
class Payment:
    value: Decimal = Decimal('0')
    description: str = "Пусто"

    def __post_init__(self):
        if self.value < 0:
            raise InvalidPaymentError("Значение должно быть положительным")


@dataclass(frozen=True, slots=True)
class Percentage(Payment):
    def __post_init__(self):
        super().__post_init__()
        if self.value > 100:
            raise InvalidPaymentError("Процент не может быть > 100")

    def apply(self, base_value: Decimal) -> Decimal:
        deduction = (self.value * base_value) / Decimal('100')
        return money_round(deduction)


@dataclass(frozen=True, slots=True)
class Fix(Payment):
    def apply(self, amount: Decimal) -> Decimal:
        return money_round(self.value)


@dataclass(frozen=True, slots=True)
class Template:
    name: str
    payments: list[Payment] = field(default_factory=list)

    def run(self, amount: Decimal):
        current_balance = amount
        total_deducted = Decimal('0')
        history = []
        fail_idx = None

        for i, payment in enumerate(self.payments):
            step = i + 1
            # FIX: always call .apply() — both Fix and Percentage implement it correctly
            deduction = payment.apply(current_balance)
            current_balance -= deduction
            total_deducted += deduction
            history.append(f"{step}. {payment.description}: -{deduction}")

            if current_balance < 0 and fail_idx is None:
                fail_idx = step

        return money_round(current_balance), history, fail_idx, money_round(total_deducted)
