from dataclasses import dataclass, field, replace
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID


class InvalidTemplateError(Exception):
    ...

class InvalidPaymentError(Exception):
    ...


@dataclass(frozen=True, slots=True)
class Bank:
    scale: Decimal = field(default=0.0)
    description: str = field(default="")
    target_scale: Decimal = field(default=0.1)

    def post_init(self)-> None:
        if self.scale < 0:
            raise InvalidPaymentError("It cant be negative")

    def target_success(self)-> None:
        if self.target_scale<=self.scale:


@dataclass(frozen=True, slots=True)
class Payment:
    value: float = field(default=0.0)
    description: str = field(default="Без описания")

    def post_init(self) -> None:
        if self.value < 0:
            raise InvalidPaymentError("Value must be positive")


@dataclass(frozen=True, slots=True)
class Percentage(Payment):

    def post_init(self) -> None:
        if self.value < 0:
            raise InvalidPaymentError("Value must be positive")

        if self.value > 100:
            raise InvalidPaymentError("Value must be less than 100")

    def apply(self, value: float) -> float:
        return value - (self.value * value) / 100

@dataclass(frozen=True, slots=True)
class Fix(Payment):

    def apply(self, amount: float) -> float:
        return amount - self.value


@dataclass(frozen=True, slots=True)
class Bank:
    amount: float = field(default=0.0)

    def post_init(self) -> None:
        if self.amount < 0:
            raise InvalidTemplateError("Amount must be positive")

    def add_money(self, amount: Payment) -> Bank:

        return replace(self, amount=amount.value + self.amount)


@dataclass(frozen=True, slots=True)
class Template:

    payments: list[Fix | Percentage] = field(default_factory=list)
    description: str = field(default="Без описания")

    def post_init(self) -> None:
        if not self.payments:
            raise ValueError("Payments list cannot be empty")

    def apply(self, amount: float) -> float:
        for payment in self.payments:
            amount = payment.apply(amount)

        return amount

money: float = 52_000
t = Template(
    payments=[
        Percentage(30),
        Fix(10_000),
        Fix(20_000),
        Fix(1_000),
    ]
)

money = t.apply(money)

print(money)