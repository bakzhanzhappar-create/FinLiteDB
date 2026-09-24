import { executeBudgetSimulation, normalizeTemplate, ValidationError } from './engine.js';
import { getAllTemplatesDB, getTemplateDB, getHistoryDB, getSettingDB, setSettingDB, saveTemplateDB, deleteTemplateDB, movePaymentDB, updateTemplatePaymentsDB, fingerprint, validateBackup, importTemplatesDB, restoreHistoryDB } from './db.js';
import { languages, currencies, translate, messages } from './i18n.js';

const $ = id => document.getElementById(id);
function readLocal(key) { try { return JSON.parse(localStorage.getItem(key)); } catch { return null; } }
const detected = navigator.language.split('-')[0];
let preferences = { language: languages[detected] ? detected : 'en', currency: 'KZT', theme: 'system', ...readLocal('finlite-preferences') };
function sanitizePreferences() {
    if (!languages[preferences.language]) preferences.language = 'en';
    if (!currencies.includes(preferences.currency)) preferences.currency = 'KZT';
    if (!['light', 'dark', 'system'].includes(preferences.theme)) preferences.theme = 'system';
}
sanitizePreferences();
let templates = [], view = 'calculate', result = null, selected = '', amount = '', draft = readLocal('finlite-draft');
if (!draft || !Array.isArray(draft.payments) || typeof draft.name !== 'string') draft = null;
if (draft) view = 'editor';
let busy = false, offlineState = 'offlinePreparing', installPrompt, waitingWorker, updateRequested = false;
const themeQuery = matchMedia('(prefers-color-scheme: dark)');
const t = (key, params) => translate(preferences.language, key, params);
function node(tag, className = '', text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = String(text);
    return element;
}
function button(label, callback, className = '', title) {
    const element = node('button', className, label);
    element.type = 'button';
    if (title) { element.title = title; element.setAttribute('aria-label', title); }
    element.addEventListener('click', () => run(callback));
    return element;
}
function field(labelText, input) { const label = node('label', '', labelText); label.append(input); return label; }
function input(value = '', props = {}) { const el = node('input'); Object.assign(el, { type: 'text', value, ...props }); return el; }
function select(options, value) {
    const el = node('select');
    for (const [id, label] of options) { const option = node('option', '', label); option.value = String(id); el.append(option); }
    el.value = value;
    return el;
}
function money(value) {
    // Keep fractional values visible even for currencies normally formatted without cents.
    const n = Number(value);
    if (!Number.isFinite(n)) return String(value);
    return new Intl.NumberFormat(preferences.language, { style: 'currency', currency: preferences.currency, minimumFractionDigits: n % 1 ? 2 : 0, maximumFractionDigits: 2 }).format(n);
}
function notice(message, error = false) {
    const box = $('notice');
    box.textContent = message;
    box.className = 'notice' + (error ? ' error' : '');
    box.setAttribute('role', error ? 'alert' : 'status');
}
function report(error) {
    console.error(error);
    const key = error instanceof ValidationError && messages.en[error.message] ? error.message : 'storageError';
    notice(t(key), true);
    $('notice').scrollIntoView({ block: 'nearest' });
}
async function run(work) {
    if (busy) return;
    busy = true;
    try { await work(); } catch (error) { report(error); }
    finally { busy = false; }
}
function persistDraft() {
    try {
        if (draft) localStorage.setItem('finlite-draft', JSON.stringify(draft));
        else localStorage.removeItem('finlite-draft');
    } catch { notice(t('storageError'), true); }
}
function applyTheme() {
    document.documentElement.dataset.theme = preferences.theme === 'system' ? (themeQuery.matches ? 'dark' : 'light') : preferences.theme;
    document.querySelector('meta[name=theme-color]').content = document.documentElement.dataset.theme === 'dark' ? '#111914' : '#f5f6f1';
}
async function savePreferences() {
    await setSettingDB('preferences', preferences);
    try { localStorage.setItem('finlite-preferences', JSON.stringify(preferences)); } catch {}
    render();
}
async function refresh() {
    templates = await getAllTemplatesDB();
    if (!templates.some(t => t.name === selected)) selected = templates[0]?.name || '';
    result = null;
}
async function changed() { await refresh(); render(); notice(t('saved')); }
function go(next) {
    view = next; render(); window.scrollTo({ top: 0, behavior: 'instant' });
}
function startEditor(template) {
    if (draft && !confirm(t('confirmDiscard'))) { go('editor'); return; }
    draft = { name: template?.name || '', originalName: template?.name || null, expected: fingerprint(template), payments: structuredClone(template?.payments || []), dirty: false };
    persistDraft(); go('editor');
}
function dirty() { draft.dirty = true; persistDraft(); }
function render() {
    applyTheme();
    document.documentElement.lang = preferences.language;
    const shell = node('div', 'shell');
    const header = node('header', 'topbar');
    const brandWrap = node('div');
    const brand = node('div', 'brand');
    brand.append(node('span', 'brand-mark', 'ƒ'), node('span', '', 'Finlite'));
    brandWrap.append(brand, node('p', 'brand-note', t('brandNote')));
    const offline = node('p', 'offline' + (offlineState === 'offlineReady' ? ' ready' : ''), t(offlineState)); offline.id = 'offline-status';
    header.append(brandWrap, offline);
    const main = node('main', 'stack'); main.id = 'main';
    const notices = node('div');
    const message = node('div', 'notice'); message.id = 'notice'; message.setAttribute('aria-live', 'polite');
    const updateBox = node('div'); updateBox.id = 'update-box'; notices.append(message, updateBox);
    shell.append(header, notices, main);
    const nav = node('nav', 'nav'); nav.setAttribute('aria-label', 'Finlite');
    for (const [tab, symbol] of [['calculate', '◴'], ['templates', '☷'], ['settings', '⚙']]) {
        const b = button('', () => go(tab)); b.dataset.view = tab;
        const icon = node('span', 'nav-symbol', symbol); icon.setAttribute('aria-hidden', 'true');
        b.append(icon, node('span', '', t(tab)));
        if (view === tab || (view === 'editor' && tab === 'templates')) b.setAttribute('aria-current', 'page');
        nav.append(b);
    }
    $('app').replaceChildren(shell, nav);
    if (view === 'calculate') renderCalculate(main);
    else if (view === 'templates') renderTemplates(main);
    else if (view === 'editor') renderEditor(main);
    else renderSettings(main);
    renderUpdate();
}
function heading(title, description) {
    const box = node('div', 'intro'); box.append(node('h1', '', title));
    if (description) box.append(node('p', 'muted', description));
    return box;
}
function emptyState() {
    const box = node('div', 'empty');
    box.append(node('span', 'empty-symbol', '+'), node('h2', '', t('empty')), node('p', 'hint', t('emptyText')), button(t('newTemplate'), () => startEditor(), 'primary'));
    return box;
}
function renderCalculate(main) {
    main.append(heading(t('intro'), t('introText')));
    if (!templates.length) { main.append(emptyState()); return; }
    const grid = node('div', 'calc-grid');
    const form = node('form', 'card stack'); form.id = 'calculate-form'; form.noValidate = true;
    const chooser = select([['', t('choose')], ...templates.map(t => [t.name, t.name])], selected); chooser.id = 'calc-template-name';
    chooser.onchange = () => { selected = chooser.value; result = null; renderCalculateResult(); };
    const amountInput = input(amount, { inputMode: 'decimal', autocomplete: 'off', placeholder: '0', className: 'amount-input', maxLength: 18 }); amountInput.id = 'calc-amount';
    amountInput.oninput = () => { amount = amountInput.value; result = null; renderCalculateResult(); };
    const amountLabel = field(t('amount') + ' · ' + preferences.currency, amountInput);
    const submit = node('button', 'primary full', t('calculate')); submit.type = 'submit'; submit.id = 'btn-calc';
    form.append(field(t('template'), chooser), amountLabel, submit, node('p', 'hint', t('percentHint')));
    form.onsubmit = event => { event.preventDefault(); run(async () => {
        const template = await getTemplateDB(selected);
        if (!template) throw new ValidationError('invalidTemplate');
        result = executeBudgetSimulation(template, amount);
        notice(''); renderCalculateResult();
        $('result').scrollIntoView({ block: 'start', behavior: 'instant' });
    }); };
    const output = node('section'); output.id = 'result'; output.setAttribute('aria-live', 'polite');
    grid.append(form, output); main.append(grid); renderCalculateResult();
}
function renderCalculateResult() {
    const output = $('result'); if (!output) return;
    output.replaceChildren();
    if (!result) { const tip = node('div', 'empty'); tip.append(node('p', 'eyebrow', t('result')), node('p', 'hint', t('simulationHint'))); output.append(tip); return; }
    const box = node('div', 'card stack');
    box.append(node('h2', '', result.template_name), node('p', 'hint', t(result.success ? 'complete' : result.history.at(-1).status === 'zero_balance_stop' ? 'zeroStop' : 'stopped')));
    const summary = node('div', 'result-summary'); summary.append(node('p', '', t('remaining')), node('p', 'big-money', money(result.final_balance)));
    const allocated = node('p', 'hint', t('amount') + ': ' + money(result.initial_amount) + ' · ' + t('allocated') + ': ' + money(result.allocated_amount));
    box.append(summary, allocated);
    const history = node('div');
    for (const row of result.history) {
        const el = node('div', 'result-row' + (row.status === 'ok' ? '' : ' failed'));
        el.append(node('h3', '', row.step + '. ' + (row.description || '—')));
        const values = node('div', 'row');
        values.append(node('span', 'money', t('allocated') + ': ' + money(row.deducted_amount)), node('span', 'hint', t('remaining') + ': ' + money(row.balance_after)));
        el.append(values);
        if (row.status !== 'ok') el.append(node('p', 'hint', t('required') + ': ' + money(row.required_amount) + ' · ' + t('shortfall') + ': ' + money(row.shortfall)));
        history.append(el);
    }
    box.append(history, node('p', 'hint', t('simulationHint'))); output.append(box);
}
function renderTemplates(main) {
    const top = node('div', 'row'); top.append(heading(t('templates')), button(t('newTemplate'), () => startEditor(), 'primary'));
    main.append(top);
    if (draft) main.append(button(t('edit') + ': ' + (draft.name || t('newTemplate')), () => go('editor'), 'full'));
    main.append(node('p', 'hint', t('percentHint')));
    if (!templates.length) { main.append(emptyState()); return; }
    const grid = node('div', 'templates-grid stack');
    for (const template of templates) {
        const card = node('article', 'card template-card'); card.dataset.template = template.name;
        const top = node('div', 'row'); top.append(node('h2', '', template.name));
        const actions = node('div', 'actions');
        actions.append(button(t('edit'), () => startEditor(template)), button(t('delete'), async () => {
            if (!confirm(t('confirmDelete', { name: template.name }))) return;
            await deleteTemplateDB(template.name, fingerprint(template)); await changed();
        }, 'danger'));
        top.append(actions); card.append(top);
        const list = node('ol', 'rule-list');
        template.payments.forEach((payment, index) => {
            const rule = node('li', 'rule');
            const line = node('div', 'rule-top');
            const info = node('div', 'rule-info');
            const percent = payment.type === 'percentage' || payment.__type__ === 'Percentage';
            info.append(node('h3', '', payment.description || '—'), node('p', 'rule-value', percent ? payment.value + '% · ' + t('percentage') : money(payment.value)));
            line.append(node('span', 'rule-number', index + 1), info); rule.append(line);
            const controls = node('div', 'rule-actions');
            const up = button('↑', async () => { await movePaymentDB(template.name, template.name, index, index - 1, fingerprint(template), fingerprint(template)); await changed(); }, 'icon-button', t('up')); up.disabled = index === 0;
            const down = button('↓', async () => { await movePaymentDB(template.name, template.name, index, index + 1, fingerprint(template), fingerprint(template)); await changed(); }, 'icon-button', t('down')); down.disabled = index === template.payments.length - 1;
            const move = button(t('move'), () => showMove(template, index)); move.disabled = templates.length < 2;
            const remove = button('×', async () => {
                if (!confirm(t('confirmDelete', { name: payment.description || String(index + 1) }))) return;
                const payments = structuredClone(template.payments); payments.splice(index, 1);
                await updateTemplatePaymentsDB(template.name, payments, fingerprint(template)); await changed();
            }, 'icon-button danger', t('delete'));
            controls.append(up, down, move, remove); rule.append(controls); list.append(rule);
        });
        card.append(template.payments.length ? list : node('p', 'hint', t('noRules'))); grid.append(card);
    }
    main.append(grid, button(t('refresh'), async () => { await refresh(); render(); }));
}
function renderEditor(main) {
    if (!draft) { view = 'templates'; renderTemplates(main); return; }
    main.append(heading(draft.originalName ? t('edit') : t('newTemplate'), t('percentHint')));
    const form = node('form', 'card stack'); form.id = 'editor-form'; form.noValidate = true;
    const name = input(draft.name, { maxLength: 100, autocomplete: 'off' }); name.id = 'tpl-name'; name.oninput = () => { draft.name = name.value; dirty(); };
    form.append(field(t('name'), name));
    const list = node('div', 'small-stack');
    draft.payments.forEach((payment, index) => {
        const row = node('div', 'draft-rule');
        const header = node('div', 'row'); header.append(node('h3', '', t('rules') + ' · ' + (index + 1)));
        const actions = node('div', 'actions');
        const reorder = to => { const [p] = draft.payments.splice(index, 1); draft.payments.splice(to, 0, p); dirty(); render(); };
        const up = button('↑', () => reorder(index - 1), 'icon-button', t('up')); up.disabled = index === 0;
        const down = button('↓', () => reorder(index + 1), 'icon-button', t('down')); down.disabled = index === draft.payments.length - 1;
        actions.append(up, down, button('×', () => { draft.payments.splice(index, 1); dirty(); render(); }, 'icon-button danger', t('delete'))); header.append(actions);
        const fields = node('div', 'editor-fields');
        const description = input(payment.description, { maxLength: 240, autocomplete: 'off' }); description.dataset.field = 'description';
        description.oninput = () => { payment.description = description.value; dirty(); };
        const descriptionLabel = field(t('ruleName'), description); descriptionLabel.className = 'wide';
        const type = select([['fix', t('fixed')], ['percentage', t('percentage')]], payment.type || (payment.__type__ === 'Percentage' ? 'percentage' : 'fix')); type.dataset.field = 'type';
        type.onchange = () => { payment.type = type.value; dirty(); };
        const value = input(payment.value, { inputMode: 'decimal', maxLength: 18, autocomplete: 'off' }); value.dataset.field = 'value';
        value.oninput = () => { payment.value = value.value; dirty(); };
        fields.append(descriptionLabel, field(t('ruleType'), type), field(t('value'), value)); row.append(header, fields); list.append(row);
    });
    const add = button('+ ' + t('addRule'), () => {
        if (draft.payments.length >= 200) throw new ValidationError('invalidTemplate');
        draft.payments.push({ type: 'fix', value: '', description: '' }); dirty(); render();
        document.querySelector('.draft-rule:last-child input').focus();
    }); add.id = 'btn-add-rule';
    const actions = node('div', 'actions');
    const save = node('button', 'primary', t('save')); save.type = 'submit'; save.id = 'btn-save-tpl';
    const cancel = button(t('cancel'), () => {
        if (draft.dirty && !confirm(t('confirmDiscard'))) return;
        draft = null; persistDraft(); go('templates');
    });
    actions.append(save, cancel); form.append(list, add, actions);
    form.onsubmit = event => { event.preventDefault(); run(async () => {
        const normalized = normalizeTemplate(draft);
        if (normalized.payments.some(p => !p.description.trim())) throw new ValidationError('invalidDescription');
        let expected = draft.expected, originalName = draft.originalName || normalized.name;
        if (!draft.originalName) {
            const existing = await getTemplateDB(normalized.name);
            if (existing) {
                if (!confirm(t('confirmReplace', { name: normalized.name }))) return;
                expected = fingerprint(existing);
            }
        } else {
            const current = await getTemplateDB(originalName);
            if (fingerprint(current) !== expected) {
                if (!confirm(t('confirmConflict', { name: originalName }))) return;
                expected = fingerprint(current);
            }
        }
        await saveTemplateDB(normalized.name, normalized.payments, expected, originalName);
        selected = normalized.name; draft = null; persistDraft(); view = 'templates'; await changed(); window.scrollTo(0, 0);
    }); };
    main.append(form);
}
function showMove(template, index) {
    const dialog = node('dialog'); dialog.id = 'move-dialog';
    const form = node('form', 'stack');
    const title = node('h2', '', t('move')); title.id = 'move-title'; dialog.setAttribute('aria-labelledby', 'move-title');
    const targets = templates.filter(t => t.name !== template.name);
    const target = select(targets.map(t => [t.name, t.name]), targets[0].name); target.id = 'move-target';
    const position = select([], ''); position.id = 'move-position';
    const updatePositions = () => {
        const template = targets.find(t => t.name === target.value);
        position.replaceChildren();
        for (let i = 0; i <= template.payments.length; i++) { const option = node('option', '', i + 1); option.value = i; position.append(option); }
        position.value = template.payments.length;
    };
    target.onchange = updatePositions; updatePositions();
    const actions = node('div', 'actions');
    const submit = node('button', 'primary', t('move')); submit.type = 'submit';
    actions.append(submit, button(t('cancel'), () => dialog.close()));
    form.append(title, field(t('template'), target), field(t('position'), position), actions);
    form.onsubmit = event => { event.preventDefault(); run(async () => {
        const destination = targets.find(t => t.name === target.value);
        try { await movePaymentDB(template.name, destination.name, index, Number(position.value), fingerprint(template), fingerprint(destination)); }
        catch (error) { dialog.close(); throw error; }
        dialog.close(); await changed();
    }); };
    dialog.onclose = () => dialog.remove(); dialog.append(form); document.body.append(dialog); dialog.showModal();
}
function renderSettings(main) {
    main.append(heading(t('settings')));
    const grid = node('div', 'settings-grid');
    const prefs = node('section', 'card stack');
    const language = select(Object.entries(languages), preferences.language); language.id = 'language'; language.onchange = () => run(async () => { preferences.language = language.value; await savePreferences(); });
    const currencyNames = new Intl.DisplayNames([preferences.language], { type: 'currency' });
    const currency = select(currencies.map(code => [code, code + ' · ' + currencyNames.of(code)]), preferences.currency); currency.id = 'currency'; currency.onchange = () => run(async () => { preferences.currency = currency.value; await savePreferences(); });
    const theme = select(['system', 'light', 'dark'].map(key => [key, t(key)]), preferences.theme); theme.id = 'theme'; theme.onchange = () => run(async () => { preferences.theme = theme.value; await savePreferences(); });
    prefs.append(field(t('language'), language), field(t('currency'), currency), node('p', 'hint', t('currencyHint')), field(t('theme'), theme));
    const backups = node('section', 'card stack'); backups.append(node('h2', '', t('backup')), node('p', 'hint', t('backupHint')));
    const exportButton = button(t('export'), exportBackup, 'primary'); exportButton.id = 'export-backup';
    const file = input('', { type: 'file', accept: '.json,application/json' }); file.id = 'import-file'; file.className = 'sr-only'; file.tabIndex = -1;
    file.onchange = () => run(async () => {
        const chosen = file.files[0]; if (!chosen) return;
        try {
            if (chosen.size > 5 * 1024 * 1024) throw new Error();
            let data;
            try { data = JSON.parse(await chosen.text()); } catch { throw new Error(); }
            const incoming = validateBackup(data);
            const current = await getAllTemplatesDB();
            const duplicates = incoming.filter(t => current.some(c => c.name === t.name)).length;
            if (!confirm(t('confirmImport', { count: incoming.length, duplicates }))) return;
            await importTemplatesDB(incoming, JSON.stringify(current)); await changed();
        } catch (error) { throw error instanceof ValidationError || error instanceof DOMException ? error : new ValidationError('invalidBackup'); }
        finally { file.value = ''; }
    });
    backups.append(exportButton, button(t('import'), () => file.click()), file);
    const install = node('section', 'card stack'); install.append(node('h2', '', t('install')), node('p', 'hint', t('installHint')));
    if (installPrompt) install.append(button(t('install'), async () => { await installPrompt.prompt(); await installPrompt.userChoice; installPrompt = null; render(); }));
    const history = node('section', 'card stack'); history.append(node('h2', '', t('history')), node('p', 'hint', t('historyHint')));
    const historyList = node('div'); historyList.id = 'history-list'; historyList.textContent = t('loading'); history.append(historyList);
    grid.append(prefs, backups, install, history); main.append(grid);
    getHistoryDB().then(items => {
        if (!historyList.isConnected) return;
        historyList.replaceChildren();
        if (!items.length) { historyList.append(node('p', 'hint', t('noHistory'))); return; }
        for (const item of items) {
            const row = node('div', 'row history-row');
            const info = node('div', 'small-stack');
            info.append(node('p', 'hint', new Intl.DateTimeFormat(preferences.language, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(item.createdAt))), node('p', '', t('templates') + ': ' + item.templates.length));
            row.append(info, button(t('restore'), async () => {
                const current = await getAllTemplatesDB();
                if (!confirm(t('confirmRestore'))) return;
                await restoreHistoryDB(item.id, JSON.stringify(current)); await changed();
            })); historyList.append(row);
        }
    }).catch(report);
}
async function exportBackup() {
    const templates = await getAllTemplatesDB();
    const data = { format: 'finlite-backup', version: 1, exportedAt: new Date().toISOString(), preferences, templates };
    const file = new File([JSON.stringify(data)], 'finlite-' + new Date().toISOString().slice(0, 10) + '.json', { type: 'application/json' });
    if (navigator.canShare?.({ files: [file] })) {
        try { await navigator.share({ files: [file], title: 'Finlite' }); notice(t('exported')); return; }
        catch (error) { if (error.name === 'AbortError') return; }
    }
    const url = URL.createObjectURL(file);
    const link = node('a'); link.href = url; link.download = file.name; document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000); notice(t('exported'));
}
function setOffline(key) {
    offlineState = key;
    const el = $('offline-status'); if (el) { el.textContent = t(key); el.className = 'offline' + (key === 'offlineReady' ? ' ready' : ''); }
}
function renderUpdate() {
    const box = $('update-box'); if (!box || !waitingWorker) return;
    const row = node('div', 'notice update-notice');
    row.append(node('span', '', t('updateReady')), button(t('update'), () => {
        persistDraft(); updateRequested = true; waitingWorker.postMessage({ type: 'ACTIVATE' });
    })); box.replaceChildren(row);
}
async function setupOffline() {
    if (!('serviceWorker' in navigator) || !isSecureContext) { setOffline('offlineFailed'); return; }
    try {
        const reg = await navigator.serviceWorker.register('./sw.js', { updateViaCache: 'none' });
        const verify = async () => {
            try {
                if (!reg.active) return;
                const ready = await new Promise(resolve => {
                    const channel = new MessageChannel();
                    const timeout = setTimeout(() => { channel.port1.close(); resolve(false); }, 4000);
                    channel.port1.onmessage = event => {
                        clearTimeout(timeout); channel.port1.close(); resolve(event.data?.ready === true);
                    };
                    reg.active.postMessage({ type: 'OFFLINE_STATUS' }, [channel.port2]);
                });
                setOffline(ready ? 'offlineReady' : 'offlineFailed');
            } catch { setOffline('offlineFailed'); }
        };
        if (reg.active) await verify();
        if (reg.waiting) { waitingWorker = reg.waiting; renderUpdate(); }
        reg.addEventListener('updatefound', () => {
            const worker = reg.installing;
            worker.addEventListener('statechange', () => {
                if (worker.state === 'installed') {
                    if (navigator.serviceWorker.controller) { waitingWorker = reg.waiting; renderUpdate(); }
                }
                if (worker.state === 'activated') verify();
                if (worker.state === 'redundant') { if (reg.active) verify(); else setOffline('offlineFailed'); }
            });
        });
        // The installation may already be underway when register() resolves.
        if (reg.installing) {
            const installing = reg.installing;
            installing.addEventListener('statechange', () => {
                if (installing.state === 'activated') verify();
                if (installing.state === 'redundant') { if (reg.active) verify(); else setOffline('offlineFailed'); }
            });
        }
        navigator.serviceWorker.addEventListener('controllerchange', () => { if (updateRequested) location.reload(); else verify(); });
        reg.update().catch(() => {});
    } catch { setOffline('offlineFailed'); }
}
window.addEventListener('beforeinstallprompt', event => { event.preventDefault(); installPrompt = event; if (view === 'settings') render(); });
window.addEventListener('appinstalled', () => { installPrompt = null; if (view === 'settings') render(); });
themeQuery.addEventListener('change', applyTheme);
window.addEventListener('beforeunload', event => { if (draft?.dirty && !updateRequested) { event.preventDefault(); event.returnValue = ''; } });
window.addEventListener('pagehide', persistDraft);
render();
(async () => {
    try {
        const stored = await getSettingDB('preferences');
        if (stored) { preferences = stored; sanitizePreferences(); }
        await refresh(); render();
        navigator.storage?.persist?.().catch(() => {});
    } catch (error) { report(error); }
    setupOffline();
})();
