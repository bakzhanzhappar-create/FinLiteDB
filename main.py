# main.py
from decimal import Decimal
from core import Template, Fix, Percentage, Bank, Validator
import storage


class FinanceOrchestrator:
    """Чистый дирижер. Только принимает, валидирует и делегирует."""

    def create_template(self, payload: dict) -> Template:
        """Делегирует создание и сохранение шаблона"""
        raw_name = payload.get("name", "Шаблон")
        raw_payments = payload.get("payments", [])

        cleaned_payments = []
        for pay in raw_payments:
            # Твой кастомный валидатор
            validated = Validator(value=pay['value'], target_type=Decimal)
            decimal_value = validated.value

            desc = pay.get('description', 'Пусто')
            p_type = pay.get('type', '').lower()

            if p_type == 'percentage':
                rule = Percentage(value=decimal_value, description=desc)
            else:
                rule = Fix(value=decimal_value, description=desc)

            cleaned_payments.append(rule)

        new_template = Template(name=raw_name, payments=cleaned_payments)
        storage.packing_to_json(new_template)
        return new_template

    def create_bank(self, payload: dict) -> Bank:
        """Делегирует создание и сохранение банка"""
        raw_name = payload.get("name", "Piggybank")
        raw_target = payload.get("target_scale", "1")
        raw_desc = payload.get("description", "")

        validated_target = Validator(value=raw_target, target_type=Decimal)

        new_bank = Bank(name=raw_name, target_scale=validated_target.value, description=raw_desc)
        storage.packing_to_json(new_bank)
        return new_bank

    def execute_calculation(self, template_name: str, raw_amount: str | float) -> dict:
        """Делегирует расчет по правилам FIFO и возвращает отчет"""
        validated_amount = Validator(value=raw_amount, target_type=Decimal)
        start_amount = validated_amount.value

        # Загружаем шаблон из твоего хранилища
        template = storage.template_from_json(template_name)

        current_balance = start_amount
        calculation_log = []
        error_at_step = None

        for idx, payment in enumerate(template.payments, start=1):
            if isinstance(payment, Percentage):
                deduction = (payment.value * start_amount) / Decimal('100')
            else:
                deduction = payment.value

            current_balance = payment.apply(current_balance)

            if current_balance < 0 and error_at_step is None:
                error_at_step = idx

            calculation_log.append({
                "step": idx,
                "type": "Фикс" if isinstance(payment, Fix) else "Проц",
                "rule_value": float(payment.value),
                "deduction": float(deduction),
                "description": payment.description
            })

        return {
            "template_name": template.name,
            "initial_amount": float(start_amount),
            "final_balance": float(current_balance),
            "success": error_at_step is None,
            "error_step": error_at_step,
            "log": calculation_log
        }