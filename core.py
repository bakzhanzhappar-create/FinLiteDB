from dataclasses import dataclass, field, replace
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID


class InvalidTemplateError(Exception):
    ...

class InvalidPaymentError(Exception):
    ...


@dataclass(frozen=True, slots=True)
class Payment:
    value: Decimal=Decimal('0')
    description: str = field(default="Без описания")

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


@dataclass(frozen=True, slots=True)
class Bank:
    amount: Decimal=Decimal('0')
    description: str = field(default="")
    target_scale: Decimal=Decimal('0')


    def __post_init__(self) -> None:
        if self.amount < 0:
            raise InvalidTemplateError("Amount must be positive")

    def add_money(self, amount: Payment) -> Bank:
        return replace(self, amount=amount.value + self.amount)

    # def target_success(self)-> None:
    #     if self.target_scale<=self.amount:

@dataclass(frozen=True, slots=True)
class Template:

    payments: list[Fix | Percentage] = field(default_factory=list)
    description: str = field(default="Без описания")

    def __post_init__(self) -> None:
        if not self.payments:
            raise ValueError("Payments list cannot be empty")

    def apply(self, amount: Decimal) -> Decimal:
        for payment in self.payments:
            amount = payment.apply(amount)
        return amount

money= Decimal('52000')
t = Template(
    payments=[
        Percentage(value=Decimal('30')),
        Fix(Decimal('10000')),
        Fix(Decimal('20000')),
        Fix(Decimal('1000')),
    ]
)

money = t.apply(money)
print(money)
print(money)