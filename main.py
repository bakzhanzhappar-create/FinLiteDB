from pydantic import BaseModel
from typing import Optional, List, Dict


# 1. Схемы данных (Валидация входящих запросов)
class TemplateItemIn(BaseModel):
    template_name: str
    item_name: str
    type: str  # "fix" или "percent"
    value: float


class BankCreateIn(BaseModel):
    name: str
    target_scale: float
    description: Optional[str] = ""


class TemplateExecIn(BaseModel):
    template_name: str
    amount: float


class BankDepositIn(BaseModel):
    bank_name: str
    amount: float


# 2. Бизнес-логика калькулятора (Твоя "золотая формула")
def calculate_template(amount: float, items: List[Dict]) -> float:
    """
    Просчитывает остаток по правилам активного шаблона.
    Сначала вычитает все фиксированные платежи, затем проценты от исходной суммы.
    """
    current_balance = amount

    # Шаг 1: Минусуем фиксы
    for item in items:
        if item.get("type") == "fix":
            current_balance -= item.get("value", 0)

    # Шаг 2: Минусуем проценты от базового дохода
    for item in items:
        if item.get("type") == "percent":
            current_balance -= (amount * (item.get("value", 0) / 100))

    return current_balance