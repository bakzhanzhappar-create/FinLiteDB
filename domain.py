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

    def withdraw(self, amount: Decimal)-> Decimal:
        if 0 < amount <= self.amount:
            self.amount -= amount
        return self.amount

    def is_target_success(self)-> bool:
        return self.target_scale<=self.amount


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

    # мешает для append, вроде некритично если шаблон пустой
    # def __post_init__(self) -> None:
    #     if not self.payments:
    #         raise ValueError("Payments list cannot be empty")

    def apply(self, amount: Decimal) -> Decimal:
        for payment in self.payments:
            amount = payment.apply(amount)
        return amount


@dataclass(slots=True)
class ApiValidator(Validator):
    """
    Наследник твоего Validator. Принимает dict из FastAPI,
    проверяет структуру вручную и возвращает объекты домена.
    """

    def to_template(self) -> Template:
        try:
            name = str(self.value.get("name", "Шаблон"))
            raw_payments = self.value.get("payments", [])

            cleaned_payments = []
            for p in raw_payments:
                # Маппинг типов из вебки (fix/percentage) в доменные
                p_type = str(p.get("type")).lower()
                val = Decimal(str(p.get("value", 0)))
                desc = str(p.get("description", "Пусто"))

                if "percent" in p_type:
                    cleaned_payments.append(Percentage(value=val, description=desc))
                else:
                    cleaned_payments.append(Fix(value=val, description=desc))

            return Template(name=name, payments=cleaned_payments)
        except (TypeError, ValueError) as e:
            raise InvalidTypeError(f"Ошибка валидации шаблона: {e}")

    def to_bank(self) -> Bank:
        try:
            name = str(self.value.get("name", "Piggybank"))
            # Маппинг фронтендового current_scale в доменный amount
            amount = Decimal(str(self.value.get("current_scale", 0)))
            target = Decimal(str(self.value.get("target_scale", 1)))
            desc = str(self.value.get("description", ""))

            return Bank(name=name, amount=amount, target_scale=target, description=desc)
        except (TypeError, ValueError) as e:
            raise InvalidTypeError(f"Ошибка валидации банка: {e}")


def execute_budget_simulation(template: Template, initial_amount: Decimal) -> dict:
    """
    Пошагово гонит сумму по правилам FIFO и собирает лог для фронтенда,
    как требовалось в твоем ТЗ (обработка нехватки средств).
    """
    current_balance = initial_amount
    success = True
    error_step = None

    for idx, payment in enumerate(template.payments, start=1):
        if isinstance(payment, Fix):
            if current_balance < payment.value:
                success = False
                error_step = idx
                break
            current_balance = payment.apply(current_balance)
        elif isinstance(payment, Percentage):
            # Процент берется от текущего остатка
            current_balance = payment.apply(current_balance)

    return {
        "template_name": template.name,
        "initial_amount": float(initial_amount),
        "final_balance": float(current_balance),
        "success": success,
        "error_step": error_step
    }