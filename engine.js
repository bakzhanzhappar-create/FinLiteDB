// Exact arithmetic: money in hundredths, percentages in hundredths of a percent.
const LIMIT = 99999999999999n;
export class ValidationError extends Error {
    constructor(code) { super(code); this.name = 'ValidationError'; }
}
export function scaled(value, percent = false) {
    if (typeof value !== 'string' && typeof value !== 'number') throw new ValidationError('invalidNumber');
    const text = String(value).trim().replace(',', '.');
    if (!/^\d+(?:\.\d{1,2})?$/.test(text) || text.length > 18) throw new ValidationError('invalidNumber');
    const [whole, fraction = ''] = text.split('.');
    const result = BigInt(whole) * 100n + BigInt(fraction.padEnd(2, '0'));
    if (result > (percent ? 10000n : LIMIT)) throw new ValidationError(percent ? 'invalidPercent' : 'invalidNumber');
    return result;
}
export function decimal(value) {
    const sign = value < 0n ? '-' : '';
    const n = value < 0n ? -value : value;
    return sign + (n / 100n) + '.' + String(n % 100n).padStart(2, '0');
}
export function normalizePayment(payment) {
    if (!payment || typeof payment !== 'object') throw new ValidationError('invalidBackup');
    const raw = payment.type ?? payment.__type__;
    const type = raw === 'Percentage' ? 'percentage' : raw === 'Fix' ? 'fix' : raw;
    if (type !== 'fix' && type !== 'percentage') throw new ValidationError('invalidType');
    if (typeof payment.description !== 'string' || payment.description.length > 240) throw new ValidationError('invalidDescription');
    return { type, __type__: type === 'percentage' ? 'Percentage' : 'Fix', value: decimal(scaled(payment.value, type === 'percentage')), description: payment.description };
}
export function normalizeTemplate(template) {
    if (!template || typeof template.name !== 'string' || !template.name.trim() || template.name.length > 100 || !Array.isArray(template.payments) || template.payments.length > 200) throw new ValidationError('invalidTemplate');
    return { name: template.name.trim(), payments: template.payments.map(normalizePayment) };
}
export class Fix {
    constructor(value, description = '') { this.value = decimal(scaled(value)); this.description = description; this.type = 'fix'; }
    apply(amount) { return decimal(scaled(amount) - scaled(this.value)); }
}
export class Percentage {
    constructor(value, description = '') { this.value = decimal(scaled(value, true)); this.description = description; this.type = 'percentage'; }
    apply(amount) { return decimal((scaled(amount) * (10000n - scaled(this.value, true)) + 5000n) / 10000n); }
}
export function executeBudgetSimulation(rawTemplate, initialAmount) {
    const template = normalizeTemplate(rawTemplate);
    const initial = scaled(initialAmount);
    let balance = initial, success = true, errorStep = null;
    const history = [];
    for (const [index, payment] of template.payments.entries()) {
        const value = scaled(payment.value, payment.type === 'percentage');
        const row = { step: index + 1, description: payment.description, type: payment.type, value: payment.value };
        if (balance === 0n && value !== 0n) {
            success = false; errorStep = index + 1;
            history.push({ ...row, deducted_amount: '0.00', balance_after: '0.00', required_amount: payment.type === 'fix' ? payment.value : '0.00', shortfall: payment.type === 'fix' ? payment.value : '0.00', status: 'zero_balance_stop' });
            break;
        }
        const after = payment.type === 'fix' ? balance - value : (balance * (10000n - value) + 5000n) / 10000n;
        if (after < 0n) {
            success = false; errorStep = index + 1;
            history.push({ ...row, deducted_amount: '0.00', balance_after: decimal(balance), required_amount: payment.value, shortfall: decimal(-after), status: 'insufficient_funds' });
            break;
        }
        history.push({ ...row, deducted_amount: decimal(balance - after), balance_after: decimal(after), shortfall: '0.00', status: 'ok' });
        balance = after;
    }
    return { template_name: template.name, initial_amount: decimal(initial), final_balance: decimal(balance), allocated_amount: decimal(initial - balance), success, error_step: errorStep, history };
}
