// db.js
// Dexie доступен глобально через CDN/скрипт в HTML
const db = new Dexie('FinliteDB');

// Объявляем таблицы (templates с первичным ключом name)
db.version(1).stores({
    templates: 'name'
});

export async function getAllTemplatesDB() {
    return await db.templates.toArray();
}

export async function getTemplateDB(name) {
    return await db.templates.get(name);
}

export async function saveTemplateDB(name, payments) {
    // В структуре сохраняем разметку __type__ для совместимости с версткой
    const formattedPayments = payments.map(p => ({
        __type__: (p.type === 'percentage' || p.__type__ === 'Percentage') ? 'Percentage' : 'Fix',
        type: p.type || (p.__type__ === 'Percentage' ? 'percentage' : 'fix'),
        value: Number(p.value),
        description: p.description
    }));

    await db.templates.put({
        name: name,
        payments: formattedPayments
    });
}

export async function deleteTemplateDB(name) {
    await db.templates.delete(name);
}

export async function updateTemplatePaymentsDB(name, newPayments) {
    await db.templates.update(name, { payments: newPayments });
}