import { normalizeTemplate, ValidationError } from './engine.js';
const NAME = 'FinliteDB'; // Keep existing Dexie data, including its native version 10.
const STORES = ['templates', 'history', 'meta'];
const request = req => new Promise((resolve, reject) => { req.onsuccess = () => resolve(req.result); req.onerror = () => reject(req.error); });
let connection;
function open(version) {
    return new Promise((resolve, reject) => {
        const req = version ? indexedDB.open(NAME, version) : indexedDB.open(NAME);
        req.onupgradeneeded = () => {
            const db = req.result;
            if (!db.objectStoreNames.contains('templates')) db.createObjectStore('templates', { keyPath: 'name' });
            if (!db.objectStoreNames.contains('history')) db.createObjectStore('history', { keyPath: 'id', autoIncrement: true });
            if (!db.objectStoreNames.contains('meta')) db.createObjectStore('meta', { keyPath: 'key' });
        };
        req.onsuccess = () => {
            const db = req.result;
            db.onversionchange = () => { db.close(); connection = undefined; };
            resolve(db);
        };
        req.onerror = () => reject(req.error);
        req.onblocked = () => {
            reject(new ValidationError('databaseBlocked'));
            req.onsuccess = () => req.result.close();
        };
    });
}
async function database() {
    if (!connection) connection = (async () => {
        let db = await open();
        if (STORES.some(s => !db.objectStoreNames.contains(s))) {
            const version = db.version + 1; db.close(); db = await open(version);
        }
        return db;
    })().catch(error => { connection = undefined; throw error; });
    return connection;
}
async function transaction(stores, mode, work) {
    const db = await database();
    const tx = db.transaction(stores, mode);
    const done = new Promise((resolve, reject) => {
        tx.oncomplete = resolve;
        tx.onabort = () => reject(tx.error || new ValidationError('storageError'));
        tx.onerror = () => {};
    });
    done.catch(() => {});
    try { const result = await work(tx); await done; return result; }
    catch (error) { try { tx.abort(); } catch {} await done.catch(() => {}); throw error; }
}
export const getAllTemplatesDB = () => transaction(['templates'], 'readonly', tx => request(tx.objectStore('templates').getAll()));
export const getTemplateDB = name => transaction(['templates'], 'readonly', tx => request(tx.objectStore('templates').get(name)));
export const getHistoryDB = () => transaction(['history'], 'readonly', async tx => (await request(tx.objectStore('history').getAll())).reverse());
export const getSettingDB = key => transaction(['meta'], 'readonly', async tx => (await request(tx.objectStore('meta').get(key)))?.value);
export const setSettingDB = (key, value) => transaction(['meta'], 'readwrite', tx => request(tx.objectStore('meta').put({ key, value })));
export const fingerprint = template => template ? JSON.stringify(template) : null;
function check(current, expected) {
    if (fingerprint(current) !== expected) throw new ValidationError('conflict');
}
async function mutate(action, work) {
    return transaction(['templates', 'history'], 'readwrite', async tx => {
        const store = tx.objectStore('templates');
        const before = await request(store.getAll());
        await work(store, tx);
        const after = await request(store.getAll());
        const bytes = templates => new TextEncoder().encode(JSON.stringify(templates)).length;
        // Keep every newly grown collection within the limits of one portable backup.
        // Existing larger legacy collections may still be reduced or deleted.
        if ((after.length > 500 && after.length > before.length) || (bytes(after) > 4 * 1024 * 1024 && bytes(after) > bytes(before))) throw new ValidationError('storageLimit');
        const history = tx.objectStore('history');
        await request(history.add({ action, createdAt: new Date().toISOString(), templates: before }));
        const keys = await request(history.getAllKeys());
        for (const key of keys.slice(0, Math.max(0, keys.length - 20))) await request(history.delete(key));
    });
}
export async function saveTemplateDB(name, payments, expected = null, originalName = name) {
    const template = normalizeTemplate({ name, payments });
    return mutate('save', async store => {
        check(await request(store.get(originalName)), expected);
        if (originalName !== template.name) {
            if (await request(store.get(template.name))) throw new ValidationError('nameExists');
            await request(store.delete(originalName));
        }
        await request(store.put(template));
    });
}
export const deleteTemplateDB = (name, expected) => mutate('delete', async store => {
    check(await request(store.get(name)), expected);
    await request(store.delete(name));
});
export const updateTemplatePaymentsDB = (name, payments, expected) => saveTemplateDB(name, payments, expected);
export const movePaymentDB = (fromName, toName, index, targetIndex, fromExpected, toExpected) => mutate('move', async store => {
    const from = await request(store.get(fromName));
    const to = fromName === toName ? from : await request(store.get(toName));
    check(from, fromExpected); check(to, toExpected);
    if (!from || !to || !Number.isInteger(index) || index < 0 || index >= from.payments.length || !Number.isInteger(targetIndex) || targetIndex < 0 || targetIndex > to.payments.length - (fromName === toName ? 1 : 0)) throw new ValidationError('invalidTemplate');
    const [payment] = from.payments.splice(index, 1);
    to.payments.splice(targetIndex, 0, payment);
    await request(store.put(normalizeTemplate(from)));
    if (from !== to) await request(store.put(normalizeTemplate(to)));
});
export function validateBackup(data) {
    if (!data || data.format !== 'finlite-backup' || data.version !== 1 || !Array.isArray(data.templates) || data.templates.length > 500) throw new ValidationError('invalidBackup');
    const templates = data.templates.map(normalizeTemplate);
    if (new Set(templates.map(t => t.name)).size !== templates.length) throw new ValidationError('invalidBackup');
    return templates;
}
export const importTemplatesDB = (templates, expected) => mutate('import', async store => {
    const normalized = validateBackup({ format: 'finlite-backup', version: 1, templates });
    if (JSON.stringify(await request(store.getAll())) !== expected) throw new ValidationError('conflict');
    for (const template of normalized) await request(store.put(template));
});
export const restoreHistoryDB = (id, expected) => mutate('restore', async (store, tx) => {
    if (JSON.stringify(await request(store.getAll())) !== expected) throw new ValidationError('conflict');
    const snapshot = await request(tx.objectStore('history').get(id));
    if (!snapshot) throw new ValidationError('invalidBackup');
    await request(store.clear());
    for (const template of snapshot.templates) await request(store.put(template));
});
