// Reject programming-style notation in maintained display mathematics.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');let equations=0;
function walk(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){if(e.isSymbolicLink()||['.git','node_modules','site','captures','objects','large'].includes(e.name))continue;const f=path.join(dir,e.name);if(e.isDirectory())walk(f);else if(f.endsWith('.md'))for(const m of fs.readFileSync(f,'utf8').matchAll(/\$\$\n([\s\S]*?)\n\$\$/g)){
  equations++;const code=m[1],where=path.relative(root,f);
  assert(!code.includes('/'),where+': use a fraction rather than a slash division');
  assert(!code.includes('\\_'),where+': use a true mathematical subscript; keep API names outside equations');
  assert(!/\\(?:mathrm|operatorname)\{(?:grad|gradient)\}/.test(code),where+': use nabla for gradients');
  assert(!/\^\(/.test(code),where+': group exponents with braces');
  assert(!/\.(?:xy|z)\b/.test(code),where+': use mathematical vector components');
}}}
walk(root);console.log(`PASS ${equations} maintained display equations: fractions, subscripts, gradients and component notation`);
