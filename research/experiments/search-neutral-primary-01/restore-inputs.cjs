// Restore indexed immutable inputs; never estimate, complete or render a source.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {zstdDecompressSync}=require('node:zlib');
const root=path.resolve(__dirname,'../../..');
const base=path.join(root,'research/experiments/agent-music-search-baseline-01');
const output=path.resolve(process.argv[2]||path.join(root,'.evidence-working/music-search-baseline-01'));
const digest=x=>crypto.createHash('sha256').update(x).digest('hex');
function write(file,bytes){fs.mkdirSync(path.dirname(file),{recursive:true});if(fs.existsSync(file)){if(!fs.readFileSync(file).equals(bytes))throw Error('Refuse conflicting input: '+file);}else fs.writeFileSync(file,bytes);}
for(const r of JSON.parse(fs.readFileSync(path.join(base,'restored-inputs.json'))).records){const bytes=zstdDecompressSync(fs.readFileSync(path.join(root,r.index_object)));if(digest(bytes)!==r.sha256)throw Error('Indexed hash mismatch');write(path.join(output,r.case,r.name),bytes);}
for(const k of ['a','b'])write(path.join(output,k,'case.json'),fs.readFileSync(path.join(base,'cases',k+'.json')));
console.log('Verified indexed inputs restored:',output);
