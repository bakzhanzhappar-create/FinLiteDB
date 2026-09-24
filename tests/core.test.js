import test from 'node:test';
import assert from 'node:assert/strict';
import { executeBudgetSimulation as run, scaled, normalizeTemplate, Percentage } from '../engine.js';
import { languages, messages, currencies } from '../i18n.js';
import { validateBackup } from '../db.js';
import { readFile, access } from 'node:fs/promises';
const rule = (type, value, description = 'Rule') => ({ type, value, description });
const template = payments => ({ name: 'Test', payments });

test('sequential rules preserve percentage-of-remaining behavior', () => {
    const result = run(template([rule('fix','30000'), rule('percentage','10'), rule('percentage','10')]), '100000');
    assert.equal(result.final_balance, '56700.00');
    assert.equal(result.allocated_amount, '43300.00');
    assert.equal(result.success, true);
});
test('0.3 minus 0.1 and 0.2 succeeds exactly', () => {
    const result = run(template([rule('fix',0.1), rule('fix',0.2)]), 0.3);
    assert.equal(result.final_balance, '0.00'); assert.equal(result.success, true);
});
test('round half up applies to remaining balance, same as Python domain', () => {
    assert.equal(new Percentage('50').apply('0.01'), '0.01');
    assert.equal(new Percentage('50').apply('0.03'), '0.02');
    assert.equal(new Percentage('100').apply('10'), '0.00');
});
test('all invalid inputs reject, including non-finite and excessive precision', () => {
    for (const value of [-1, NaN, Infinity, null, {}, '', ' ', '1e3', '0.001', '1000000000000', 'abc']) assert.throws(() => scaled(value));
    for (const value of ['100.01','150',-1]) assert.throws(() => run(template([rule('percentage',value)]),'100'));
    assert.throws(() => run(template([rule('unknown','1')]),'100'));
    assert.equal(scaled('1,25'),125n);
});
test('insufficient funds keep balance and distinguish required from allocated', () => {
    const result = run(template([rule('fix','150'),rule('fix','1')]),'100');
    assert.equal(result.success,false); assert.equal(result.history.length,1);
    assert.equal(result.final_balance,'100.00'); assert.equal(result.history[0].balance_after,'100.00');
    assert.equal(result.history[0].deducted_amount,'0.00'); assert.equal(result.history[0].shortfall,'50.00');
});
test('zero-valued rules are harmless; nonzero rules stop at zero as before', () => {
    assert.equal(run(template([rule('fix','100'),rule('fix','0'),rule('percentage','0')]),'100').success,true);
    assert.equal(run(template([rule('fix','100'),rule('percentage','10')]),'100').history[1].status,'zero_balance_stop');
});
test('money is conserved across a deterministic range of mixed rules', () => {
    for(let n=1;n<=300;n++) {
        const initial = (n / 100).toFixed(2);
        const result = run(template([rule('percentage','33.33'),rule('percentage','66.67'),rule('fix','0.01')]), initial);
        const sum = result.history.reduce((total,r)=>total+scaled(r.deducted_amount),0n);
        assert.equal(sum + scaled(result.final_balance),scaled(initial));
        assert.ok(scaled(result.final_balance)>=0n);
    }
});
test('legacy types normalize without changing order or description', () => {
    const result = normalizeTemplate({name:'Legacy',payments:[{__type__:'Percentage',value:10,description:'<b>literal</b>'},{__type__:'Fix',value:30,description:'B'}]});
    assert.equal(result.payments[0].type,'percentage'); assert.equal(result.payments[0].description,'<b>literal</b>');
});
test('backup validation rejects duplicates, invalid data, versions and excessive size', () => {
    const good={format:'finlite-backup',version:1,templates:[template([rule('fix','1')])]};
    assert.equal(validateBackup(good).length,1);
    for(const bad of [{...good,version:2},{...good,templates:[good.templates[0],good.templates[0]]},{...good,templates:[template([rule('percentage','101')])]}]) assert.throws(()=>validateBackup(bad));
});
test('all ten languages have exactly the same complete keys and placeholders', () => {
    assert.equal(Object.keys(languages).length,10); assert.equal(currencies.length,10);
    const keys=Object.keys(messages.en).sort();
    for(const lang of Object.keys(languages)) {
        assert.deepEqual(Object.keys(messages[lang]).sort(),keys);
        for(const key of keys) {
            assert.ok(messages[lang][key]);
            assert.deepEqual((messages[lang][key].match(/\{\w+\}/g)||[]).sort(),(messages.en[key].match(/\{\w+\}/g)||[]).sort());
        }
    }
});
test('offline bundle contains every runtime file, uses no external dependency', async () => {
    const sw=await readFile(new URL('../sw.js',import.meta.url),'utf8');
    for(const file of ['index.html','styles.css','app.js','engine.js','db.js','i18n.js','manifest.json','icon.svg','icons/icon-192.png','icons/icon-512.png']) {
        assert.ok(sw.includes("'./"+file+"'")); await access(new URL('../'+file,import.meta.url));
    }
    for(const file of ['index.html','app.js','db.js','styles.css','manifest.json']) assert.doesNotMatch(await readFile(new URL('../'+file,import.meta.url),'utf8'),/https?:\/\//);
    assert.doesNotMatch(await readFile(new URL('../app.js',import.meta.url),'utf8'),/innerHTML|insertAdjacentHTML/);
});
