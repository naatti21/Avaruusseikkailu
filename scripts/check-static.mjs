import {readFileSync,existsSync} from 'node:fs';
import assert from 'node:assert/strict';
const files=['index.html','styles.css','app.mjs','game-core.mjs','sw.js','manifest.webmanifest'];
for(const f of files)assert.ok(existsSync(f),'Missing '+f);
const html=readFileSync('index.html','utf8');
for(const id of ['viewport','space','overlay','panel','actions','naming','where','credits','fuel','distance','notice'])assert.ok(html.includes('id="'+id+'"'),'Missing UI '+id);
assert.ok(!/https?:\/\/.*(cdn|jsdelivr|unpkg)/i.test(html),'Prototype must not depend on a CDN');
JSON.parse(readFileSync('manifest.webmanifest','utf8'));
console.log('Static files and manifest: OK');