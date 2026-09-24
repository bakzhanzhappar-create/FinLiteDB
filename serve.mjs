import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
const root = new URL('./', import.meta.url);
const types = { html: 'text/html; charset=utf-8', css: 'text/css; charset=utf-8', js: 'text/javascript; charset=utf-8', json: 'application/json', svg: 'image/svg+xml', png: 'image/png' };
const allowed = new Set(['index.html','styles.css','app.js','engine.js','db.js','i18n.js','sw.js','manifest.json','icon.svg','icons/icon-192.png','icons/icon-512.png']);
export function startServer(port = 4173, overrides = new Map()) {
    return new Promise(resolve => {
        const server = http.createServer(async (req, res) => {
            const path = new URL(req.url, 'http://localhost').pathname.slice(1) || 'index.html';
            if (!allowed.has(path)) { res.writeHead(404); res.end('Not found'); return; }
            try {
                const data = overrides.get(path) ?? await readFile(new URL(path, root));
                res.writeHead(200, { 'Content-Type': types[path.split('.').at(-1)], 'Cache-Control': 'no-cache', 'X-Content-Type-Options': 'nosniff' });
                res.end(data);
            } catch { res.writeHead(404); res.end('Not found'); }
        });
        server.listen(port, '127.0.0.1', () => resolve(server));
    });
}
if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
    const server = await startServer(Number(process.env.PORT || 4173));
    console.log('Finlite: http://127.0.0.1:' + server.address().port);
}
