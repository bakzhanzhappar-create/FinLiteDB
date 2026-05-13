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
class Bank:
    amount: Decimal=Decimal('0')
    description: str = field(default="")
    target_scale: Decimal=Decimal('1')
    name: str=field(default="Piggybank")

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise InvalidPaymentError("Amount must be positive")

        if self.target_scale < 0:
            raise InvalidPaymentError("Target scale must be positive")


    def add_money(self, amount: Decimal) -> Decimal:
        self.amount +=amount
        self.amount=self.amount.quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)
        return self.amount

    # def give_money(self, amount: Decimal)-> Decimal:
    #     self.amount -= amount
    #     return self.amount
    # крч прописать передачу денег другому сущности (шаблону или банку)

    def is_target_success(self)-> bool:
        return self.target_scale<=self.amount


@dataclass(slots=True)
class Validator:
    value: str | Decimal
    target_type: type = Decimal

    def __post_init__(self) -> None:
        try:
            self.value=self.target_type(self.value)
        except TypeError:
            raise InvalidTypeError(f" {self.value} тут есть некорректный символ")


@dataclass(frozen=True, slots=True)
class Template:

    payments: list[Fix | Percentage] = field(default_factory=list)
    name: str = field(default="Шаблон")

    def __post_init__(self) -> None:
        if not self.payments:
            raise ValueError("Payments list cannot be empty")

    def apply(self, amount: Decimal) -> Decimal:
        for payment in self.payments:
            amount = payment.apply(amount)
        return amount


# scholarship= Decimal('52367')
# t=Template(
#     payments=[
#         Fix(Decimal('1320'), description="за проезд"),
#         Fix(Decimal('5790'), description="за тариф"),
#         Fix(Decimal('5000'), description="сестренке"),
#         Fix(Decimal('28000'), description="на все про все"),
#         Fix(Decimal('12257'), description="самоналог"),
#     ])
# scholarship=t.apply(scholarship)
# print(scholarship)
#
# for i in t.payments:
#     print(i)

# money= Decimal('52000')
# t = Template(
#     payments=[
#         Fix(Decimal('10000'), "coca cola"),
#         Fix(Decimal('20000')),
#         Fix(Decimal('1000')),
#         Percentage(value=Decimal('30')),
#     ],
#     name ="for foods"
# )
#
# money = t.apply(money)
# print(money)
# print(t.name)
# print(t.payments[1].description)

money_for_bank=Decimal('111.8998')
b= Bank(
    name="Lada",
    target_scale=Decimal('45000'),
    description="Once i have a dream that one day ill move w niggas to diff cities"
)

c=Bank(
    name="111111Lada",
    target_scale=Decimal('45000'),
    description="Once i have a dream that one day ill move w niggas to diff cities"
)
money_for_bank=b.add_money(money_for_bank)
print(money_for_bank)
print(b.description)
print(b.amount)
print(b.is_target_success())

m1=Decimal('123.17658857')
money_for_bank=b.add_money(m1)
print(b.amount)
