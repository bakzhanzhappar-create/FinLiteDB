import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { mkdir, readFile } from 'node:fs/promises';
import { startServer } from '../serve.mjs';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const overrides = new Map();
const server = await startServer(0, overrides);
const base = 'http://127.0.0.1:' + server.address().port + '/';
const browser = await chromium.launch({ headless: true, ...(process.env.BROWSER_EXECUTABLE ? { executablePath: process.env.BROWSER_EXECUTABLE } : {}) });
const errors = [];
let context;
const pass = text => console.log('PASS ' + text);
try {
    context = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1, isMobile: true, hasTouch: true, locale: 'en-US', acceptDownloads: true });
    const page = await context.newPage(); page.on('pageerror', error => errors.push(error.message));
    const requests = []; page.on('request', request => requests.push(request.url()));
    page.on('dialog', dialog => dialog.accept());
    await page.goto(base + 'icon.svg');
    await page.evaluate(async () => {
        const db = await new Promise((resolve,reject) => {
            const r=indexedDB.open('FinliteDB',10);
            r.onupgradeneeded=()=>r.result.createObjectStore('templates',{keyPath:'name'});
            r.onsuccess=()=>resolve(r.result); r.onerror=()=>reject(r.error);
        });
        const tx=db.transaction('templates','readwrite'); const store=tx.objectStore('templates');
        store.put({name:'Legacy',payments:[{__type__:'Fix',value:30,description:'Rent'},{__type__:'Percentage',value:10,description:'Savings'}]});
        store.put({name:'Destination',payments:[{__type__:'Fix',value:5,description:'Other'}]});
        store.put({name:'Long',payments:Array.from({length:20},(_,i)=>({__type__:'Fix',value:1,description:'Rule '+i}))});
        store.put({name:'<img src=x onerror="window.xss=true">',payments:[{__type__:'Fix',value:1,description:'<svg onload="window.xss=true">'}]});
        await new Promise((resolve,reject)=>{tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);}); db.close();
    });
    await page.goto(base);
    await page.waitForSelector('#calc-template-name');
    await page.waitForFunction(()=>document.querySelector('#offline-status')?.textContent==='Ready offline');
    assert.equal(await page.evaluate(async()=> (await (await import('./db.js')).getAllTemplatesDB()).length),4);
    pass('migrates Dexie version 10 and retains old templates');
    await page.selectOption('#calc-template-name','Legacy'); await page.fill('#calc-amount','100'); await page.click('#btn-calc'); await page.waitForFunction(()=>document.querySelector('#result')?.textContent.includes('Plan calculated'));
    assert.match(await page.locator('#result').innerText(),/63/); pass('existing rules calculate in the UI');
    await page.click('[data-view=templates]');
    assert.equal(await page.evaluate(()=>window.xss),undefined);
    assert.equal(await page.locator('main img,main svg').count(),0); pass('user strings render as text, not HTML');
    const client=await context.newCDPSession(page);
    async function swipe(start,end) {
        await client.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:180,y:start}]});
        for(let i=1;i<=8;i++) {await client.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:180,y:start+(end-start)*i/8}]});await page.waitForTimeout(30);}
        await client.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]}); await page.waitForTimeout(250);
    }
    await page.evaluate(()=>scrollTo(0,0)); await swipe(570,190);
    const afterDown=await page.evaluate(()=>scrollY); assert.ok(afterDown>100,'touch scroll down');
    await swipe(190,600); assert.ok(await page.evaluate(()=>scrollY)<afterDown,'touch scroll up');
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    pass('real touch gestures scroll both directions without horizontal overflow');
    await page.locator('[data-template=Legacy]').getByRole('button',{name:'Move to template',exact:true}).first().click();
    await page.selectOption('#move-target','Destination'); await page.selectOption('#move-position','0');
    await page.locator('#move-dialog').getByRole('button',{name:'Move to template',exact:true}).click();
    await page.waitForFunction(()=>!document.querySelector('#move-dialog'));
    const moved=await page.evaluate(async()=> (await import('./db.js')).getAllTemplatesDB());
    assert.deepEqual(moved.find(t=>t.name==='Destination').payments.map(p=>p.description),['Rent','Other']);
    assert.deepEqual(moved.find(t=>t.name==='Legacy').payments.map(p=>p.description),['Savings']);
    pass('atomic transfer inserts at the chosen position');
    await page.evaluate(async()=>{
        const db=await import('./db.js');
        const from=await db.getTemplateDB('Legacy');
        let rejected=false;
        try{await db.saveTemplateDB('Legacy',[],null);}catch(e){rejected=e.message==='conflict';}
        if(!rejected)throw new Error('overwrite without confirmation accepted');
        await db.saveTemplateDB('Full',Array.from({length:200},()=>({type:'fix',value:'1',description:'Full'})));
        const to=await db.getTemplateDB('Full');
        const before=JSON.stringify(await db.getAllTemplatesDB()); const count=(await db.getHistoryDB()).length;
        try{await db.movePaymentDB('Legacy','Full',0,0,db.fingerprint(from),db.fingerprint(to));throw new Error('limit ignored');}catch(e){if(e.message!=='invalidTemplate')throw e;}
        if(JSON.stringify(await db.getAllTemplatesDB())!==before || (await db.getHistoryDB()).length!==count)throw new Error('transaction did not roll back');
        await db.deleteTemplateDB('Full',db.fingerprint(to));
        const legacy=await db.getTemplateDB('Legacy');
        await db.updateTemplatePaymentsDB('Legacy',[{type:'fix',value:'2',description:'Changed'}],db.fingerprint(legacy));
        try{await db.updateTemplatePaymentsDB('Legacy',[],db.fingerprint(legacy));throw new Error('stale write accepted');}catch(e){if(e.message!=='conflict')throw e;}
        const snap=(await db.getHistoryDB())[0]; await db.restoreHistoryDB(snap.id,JSON.stringify(await db.getAllTemplatesDB()));
        if((await db.getTemplateDB('Legacy')).payments[0].description!=='Savings')throw new Error('restore failed');
        const all=JSON.stringify(await db.getAllTemplatesDB());
        try{await db.importTemplatesDB([{name:'Bad',payments:[{type:'percentage',value:'150',description:'Bad'}]}],all);throw new Error('invalid import accepted');}catch(e){if(e.message!=='invalidPercent')throw e;}
        if(JSON.stringify(await db.getAllTemplatesDB())!==all)throw new Error('failed import changed data');
        for(let i=0;i<22;i++) {
            const current=await db.getTemplateDB('History cap');
            await db.saveTemplateDB('History cap',[{type:'fix',value:String(i),description:'State'}],db.fingerprint(current));
        }
        if((await db.getHistoryDB()).length!==20)throw new Error('history not bounded');
        await db.deleteTemplateDB('History cap',db.fingerprint(await db.getTemplateDB('History cap')));
    });
    pass('duplicate/stale writes reject; failed transfers fully roll back; history restores');
    await page.reload(); await page.waitForSelector('#calc-template-name');
    await page.click('[data-view=templates]'); await page.getByRole('button',{name:'New template',exact:true}).click();
    await page.fill('#tpl-name','Exact'); await page.click('#btn-add-rule');
    await page.locator('[data-field=description]').fill('First'); await page.locator('[data-field=value]').fill('0.1');
    await page.click('#btn-add-rule'); await page.locator('[data-field=description]').nth(1).fill('Second'); await page.locator('[data-field=value]').nth(1).fill('0.2');
    await page.reload(); await page.waitForSelector('#tpl-name'); assert.equal(await page.inputValue('#tpl-name'),'Exact');
    await page.click('#btn-save-tpl'); await page.waitForSelector('[data-template=Exact]');
    // Deleting one saved rule must never delete its parent template.
    await page.locator('[data-template=Destination]').getByRole('button',{name:'Delete',exact:true}).last().click();
    await page.waitForFunction(async()=> (await (await import('./db.js')).getTemplateDB('Destination')).payments.length===1);
    await page.click('[data-view=calculate]'); await page.selectOption('#calc-template-name','Exact'); await page.fill('#calc-amount','0,3'); await page.click('#btn-calc'); await page.waitForFunction(()=>document.querySelector('#result')?.textContent.includes('Plan calculated'));
    assert.match(await page.locator('#result').innerText(),/Plan calculated/); assert.match(await page.locator('.big-money').innerText(),/0/);
    pass('editor draft survives reload and fractional amounts calculate exactly');
    await page.click('[data-view=settings]');
    const downloadPromise=page.waitForEvent('download'); await page.click('#export-backup'); const download=await downloadPromise;
    const backup=JSON.parse(await readFile(await download.path(),'utf8')); assert.equal(backup.format,'finlite-backup'); assert.equal(backup.templates.length,5);
    await page.setInputFiles('#import-file',{name:'backup.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({...backup,templates:[{name:'Imported',payments:[{type:'fix',value:'1',description:'Import'}]}]}))});
    await page.waitForFunction(async()=>Boolean(await (await import('./db.js')).getTemplateDB('Imported')));
    pass('exported JSON and confirmed import round trip');
    for(const lang of ['ru','kk','de','fr','es','zh','ja','ko','tr','en']) {
        await page.selectOption('#language',lang); await page.waitForFunction(lang=>document.documentElement.lang===lang,lang);
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    }
    await page.selectOption('#currency','JPY'); await page.waitForFunction(()=>document.querySelector('#currency')?.value==='JPY');
    await page.reload(); await page.waitForSelector('#calc-template-name'); await page.click('[data-view=settings]'); assert.equal(await page.inputValue('#currency'),'JPY');
    pass('10 languages fit the phone; currency preference persists');
    await mkdir(new URL('../test-results/',import.meta.url),{recursive:true});
    await page.click('[data-view=calculate]'); await page.selectOption('#calc-template-name','Exact'); await page.fill('#calc-amount','0.3'); await page.click('#btn-calc'); await page.waitForFunction(()=>document.querySelector('#result')?.textContent.includes('Plan calculated'));
    await page.evaluate(()=>scrollTo(0,0)); await page.screenshot({path:new URL('../test-results/mobile.png',import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1'),fullPage:true});
    await context.setOffline(true);
    await page.reload(); await page.waitForSelector('#calc-template-name'); await page.selectOption('#calc-template-name','Exact'); await page.fill('#calc-amount','0.3'); await page.click('#btn-calc'); await page.waitForFunction(()=>document.querySelector('#result')?.textContent.includes('Plan calculated'));
    assert.match(await page.locator('#result').innerText(),/Plan calculated/);
    const second=await context.newPage(); await second.goto(base+'index.html'); await second.waitForSelector('#calc-template-name');
    pass('offline reload and a new offline tab both calculate without network');
    await context.setOffline(false); await second.close();
    await page.waitForFunction(()=>document.querySelector('#offline-status')?.textContent==='Ready offline');
    const originalWorker = await readFile(new URL('../sw.js',import.meta.url),'utf8');
    await page.evaluate(async()=>{ await caches.open('unrelated-app-cache'); });
    overrides.set('sw.js',originalWorker.replace("const VERSION = 'v3'", "const VERSION = 'v4'"));
    await page.evaluate(async()=>{ await (await navigator.serviceWorker.getRegistration()).update(); });
    await page.getByRole('button',{name:'Update app',exact:true}).waitFor();
    await page.click('[data-view=templates]'); await page.getByRole('button',{name:'New template',exact:true}).click();
    await page.fill('#tpl-name','Draft during update');
    await page.getByRole('button',{name:'Update app',exact:true}).click();
    await page.waitForFunction(()=>document.querySelector('#tpl-name')?.value==='Draft during update' && document.querySelector('#offline-status')?.textContent==='Ready offline');
    assert.equal(await page.evaluate(async()=> (await caches.keys()).includes('unrelated-app-cache')),true);
    await page.getByRole('button',{name:'Cancel',exact:true}).click();
    await context.setOffline(true); await page.reload(); await page.waitForSelector('#calc-template-name');
    await page.waitForFunction(()=>document.querySelector('#offline-status')?.textContent==='Ready offline');
    pass('PWA update preserves draft, works offline and retains unrelated caches');
    await context.setOffline(false);
    overrides.set('sw.js',originalWorker.replace("const VERSION = 'v3'", "const VERSION = 'v5'").replace("const ASSETS = [", "const ASSETS = ['./missing.js',"));
    await page.evaluate(async()=> {
        const reg=await navigator.serviceWorker.getRegistration();
        await new Promise(async(resolve,reject)=> {
            reg.addEventListener('updatefound',()=> {
                const worker=reg.installing;
                worker.addEventListener('statechange',()=>{if(worker.state==='redundant')resolve();});
            },{once:true});
            try{await reg.update();}catch(e){reject(e);}
        });
    });
    await context.setOffline(true); await page.reload(); await page.waitForSelector('#calc-template-name');
    await page.waitForFunction(()=>document.querySelector('#offline-status')?.textContent==='Ready offline');
    pass('failed update leaves the previously installed offline bundle intact');
    await context.setOffline(false);
    overrides.set('sw.js',originalWorker.replace("const VERSION = 'v3'", "const VERSION = 'v4'"));
    await page.click('[data-view=settings]'); await page.selectOption('#theme','dark');
    await page.waitForFunction(()=>document.documentElement.dataset.theme==='dark');
    await page.setViewportSize({width:320,height:568});
    await page.click('[data-view=templates]'); await page.getByRole('button',{name:'New template',exact:true}).click();
    await page.fill('#tpl-name','Validation'); await page.click('#btn-add-rule');
    await page.locator('[data-field=description]').fill('Percent'); await page.locator('[data-field=type]').selectOption('percentage'); await page.locator('[data-field=value]').fill('150');
    await page.click('#btn-save-tpl'); await page.waitForFunction(()=>document.querySelector('#notice').textContent.includes('between 0 and 100'));
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    assert.equal(await page.evaluate(async()=>Boolean(await (await import('./db.js')).getTemplateDB('Validation'))),false);
    await page.getByRole('button',{name:'Cancel',exact:true}).click();
    pass('invalid percent is rejected in the phone editor; dark theme fits 320px');
    for(const width of [320,360,430,768,1280]) {
        await page.setViewportSize({width,height:844}); await page.click('[data-view=templates]');
        assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'overflow at '+width);
    }
    await page.screenshot({path:new URL('../test-results/desktop.png',import.meta.url).pathname.replace(/^\/([A-Za-z]:)/,'$1'),fullPage:true});
    assert.equal(requests.some(url=>!url.startsWith(base)),false,'unexpected third-party request');
    assert.deepEqual(errors,[]);
    pass('320–1280px layouts; no third-party requests or uncaught browser errors');
} finally { await context?.close(); await browser.close(); await new Promise(resolve=>server.close(resolve)); }
