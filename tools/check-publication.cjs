// Documentation is readable on the site, with no Markdown-host detours.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),site=path.join(root,'guide/site');
const manifest=JSON.parse(fs.readFileSync(path.join(site,'build.json')));
let html=0;
for(const file of Object.keys(manifest.files).filter(f=>f.endsWith('.html'))){
  const text=fs.readFileSync(path.join(site,file),'utf8');
  for(const m of text.matchAll(/href="([^"]+)"/g))assert(!/^https?:\/\/(?:github\.com|raw\.githubusercontent\.com)\/[^"\s]+\.md(?:[?#]|$)/i.test(m[1]),file+': Markdown must have a rendered page: '+m[1]);
  html++;
}
function walk(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){if(e.isSymbolicLink()||['.git','node_modules','site','captures','objects','large'].includes(e.name))continue;const f=path.join(dir,e.name);if(e.isDirectory())walk(f);else if(f.endsWith('.md')){const rel=path.relative(root,f).split(path.sep).join('/');assert(manifest.documentation.some(d=>d.source===rel),'Unpublished documentation: '+rel);}}}
walk(root);
assert(manifest.documentation.some(d=>d.source==='research/evidence/catalogue.md'));
console.log(`PASS ${manifest.documentation.length} maintained documents published; ${html} HTML pages without Markdown-host detours`);
