// Аналоги классов Fix и Percentage из domain.py
export class Fix {
    constructor(value, description = "Пусто") {
        this.value = Number(value);
        this.description = description;
        this.type = "fix";
    }

    apply(amount) {
        return amount - this.value;
    }
}

export class Percentage {
    constructor(value, description = "Пусто") {
        this.value = Number(value);
        this.description = description;
        this.type = "percentage";
    }

    apply(amount) {
        const result = amount - (this.value * amount) / 100;
        // Округление до 2 знаков после запятой (аналог ROUND_HALF_UP)
        return Math.round(result * 100) / 100;
    }
}

// Аналог execute_budget_simulation из domain.py
export function executeBudgetSimulation(template, initialAmount) {
    let currentBalance = Number(initialAmount);
    let success = true;
    let errorStep = null;
    const history = [];

    for (let index = 0; index < template.payments.length; index++) {
        const step = index + 1;
        const pData = template.payments[index];

        // Восстанавливаем экземпляр класса (Fix или Percentage)
        const payment = pData.type === 'percentage' || pData.__type__ === 'Percentage'
            ? new Percentage(pData.value, pData.description)
            : new Fix(pData.value, pData.description);

        if (currentBalance === 0) {
            success = false;
            errorStep = step;
            history.push({
                step,
                description: payment.description,
                type: payment.type,
                value: payment.value,
                deducted_amount: 0,
                balance_after: 0,
                status: "zero_balance_stop"
            });
            break;
        }

        if (payment instanceof Fix) {
            const deducted = payment.value;
            const balanceAfter = payment.apply(currentBalance);

            if (currentBalance < payment.value) {
                success = false;
                errorStep = step;
                history.push({
                    step,
                    description: payment.description,
                    type: payment.type,
                    value: payment.value,
                    deducted_amount: deducted,
                    balance_after: balanceAfter,
                    status: "insufficient_funds"
                });
                break;
            }

            currentBalance = balanceAfter;
            history.push({
                step,
                description: payment.description,
                type: payment.type,
                value: payment.value,
                deducted_amount: deducted,
                balance_after: currentBalance,
                status: "ok"
            });

        } else if (payment instanceof Percentage) {
            const balanceAfter = payment.apply(currentBalance);
            const deducted = Math.round((currentBalance - balanceAfter) * 100) / 100;
            currentBalance = balanceAfter;

            history.push({
                step,
                description: payment.description,
                type: payment.type,
                value: payment.value,
                deducted_amount: deducted,
                balance_after: currentBalance,
                status: "ok"
            });
        }
    }

    return {
        template_name: template.name,
        initial_amount: Number(initialAmount),
        final_balance: currentBalance,
        success,
        error_step: errorStep,
        history
    };
}