const fs=require('fs'),path=require('path'),cp=require('child_process'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..'),base=path.join(root,'.evidence-working/compact-geometry-01');
const index=JSON.parse(fs.readFileSync(path.join(root,'research/evidence/index.json')));
const capture=path.join(root,'research/captures/dark-glass-lab/extended/helper-toolbar-work/compact-mini-round');
const prior=JSON.parse(fs.readFileSync(path.join(root,'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json')));
const paired=path.join(root,'reconstruction/studies/music-mini-compact-vector/paired'),state=JSON.parse(fs.readFileSync(path.join(paired,'accepted.json')));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const canonical=x=>Array.isArray(x)?x.map(canonical):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,canonical(x[k])])):x;
function write(file,bytes){if(fs.existsSync(file)&&sha(fs.readFileSync(file))!==sha(bytes))throw Error('Different local input');fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,bytes);}
const records=[];
for(const k of ['a','b']){
 const bytes=fs.readFileSync(path.join(capture,k,'case.json')),c=JSON.parse(bytes),standard=JSON.parse(fs.readFileSync(path.join(paired,k+'.json')));
 for(const name of ['foreground_styles','foreground_response'])if(state[name])standard[name]=state[name];
 if(JSON.stringify(canonical(c))!==JSON.stringify(canonical(standard)))throw Error('Case semantics differ from public paired snapshot');
 write(path.join(base,k,'case.json'),bytes);
 const inputs={...c.source_sha256};
 for(const layer of c.foreground_layers){if(layer.vector_asset){if(layer.vector_sha256!==prior.vector_sha256[k][layer.vector_asset])throw Error('Vector changed');inputs[layer.vector_asset]=layer.vector_sha256;}if(layer.artwork_asset)inputs[layer.artwork_asset]=layer.artwork_sha256;}
 const hashes={};
 for(const [name,digest] of Object.entries(inputs)){
  if(path.basename(name)!==name)throw Error('Unsafe input name');const r=index.logical_files.find(r=>r.sha256===digest&&r.object);if(!r)throw Error('Missing indexed input');
  const data=cp.execFileSync('zstd',['-q','-d','-c','--',path.join(root,r.object)],{maxBuffer:Math.max(r.bytes+1048576,8*1024*1024)});
  if(data.length!==r.bytes||sha(data)!==digest)throw Error('Input mismatch');write(path.join(base,k,name),data);hashes[name]=digest;
 }
 records.push({reference:k,case_sha256:sha(bytes),case_matches_public_paired_semantics:true,historical_byte_receipt_matches:sha(bytes)===prior.case_sha256[k],hashes});
}
fs.writeFileSync(path.join(__dirname,'inputs.json'),JSON.stringify({records,source_changed:false,registration_changed:false,foreground_changed:false},null,2)+'\n');
console.log('Both cases, sources, vectors and artwork verified.');
