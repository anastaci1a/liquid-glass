#!/usr/bin/env node
// Restore only the declared inputs; never replace different local bytes.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),cp=require('child_process');
const root=path.resolve(__dirname,'../../..');
const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'restored-inputs.json')));
const index=JSON.parse(fs.readFileSync(path.join(root,'research/evidence/index.json')));
const base=path.join(root,'.evidence-working/clear-play-02');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
for(const item of manifest.files){
 const target=path.resolve(base,item.logical);
 if(!target.startsWith(base+path.sep))throw Error('Unsafe input path');
 if(fs.existsSync(target)){
  const bytes=fs.readFileSync(target);
  if(bytes.length!==item.bytes||sha(bytes)!==item.sha256)throw Error('Different local input: '+item.logical);
  continue;
 }
 const record=index.logical_files.find(r=>r.sha256===item.sha256&&r.object&&r.bytes===item.bytes);
 if(!record)throw Error('Missing indexed input: '+item.logical);
 const object=path.resolve(root,record.object);
 if(!object.startsWith(root+path.sep))throw Error('Unsafe object path');
 const bytes=cp.execFileSync('zstd',['-q','-d','-c','--',object],{maxBuffer:Math.max(item.bytes+1048576,64*1024*1024)});
 if(bytes.length!==item.bytes||sha(bytes)!==item.sha256)throw Error('Evidence digest mismatch');
 fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,bytes,{flag:'wx'});
}
console.log('Verified '+manifest.files.length+' declared inputs.');
