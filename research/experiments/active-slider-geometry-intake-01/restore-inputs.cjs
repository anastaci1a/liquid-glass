// Restore only the pinned, already-indexed inputs. No source estimation or rendering.
const fs=require('node:fs'), path=require('node:path'), cp=require('node:child_process'), crypto=require('node:crypto');
const packet=__dirname, root=path.resolve(packet,'../../..');
const store=process.argv[2] ? path.resolve(process.argv[2]) : root;
const manifest=JSON.parse(fs.readFileSync(path.join(packet,'evidence-manifest.json')));
const hash=data=>crypto.createHash('sha256').update(data).digest('hex');
process.umask(0o002);
for(const key of ['a','b']){
 const frozen=fs.readFileSync(path.join(packet,'frozen-records',`paired--${key}.json`));
 const spec=JSON.parse(frozen), folder=path.join(packet,'baseline/inputs',key);
 fs.mkdirSync(folder,{recursive:true});
 for(const [name,original] of Object.entries(spec.input_names)){
  const record=manifest.find(r=>r.logical.endsWith('/'+original));
  if(!record || record.sha256!==spec.source_sha256[name]) throw Error('Manifest disagreement: '+name);
  const data=cp.execFileSync('zstd',['-q','-d','-c','--',path.join(store,record.object)],{maxBuffer:64*1024*1024});
  if(hash(data)!==record.sha256 || data.length!==record.bytes)throw Error('Input hash mismatch: '+name);
  const dest=path.join(folder,name);
  if(fs.existsSync(dest)){if(hash(fs.readFileSync(dest))!==record.sha256)throw Error('Existing input differs: '+dest);}
  else fs.writeFileSync(dest,data);
 }
 const dest=path.join(folder,'case.json');
 if(fs.existsSync(dest)){if(!fs.readFileSync(dest).equals(frozen))throw Error('Existing case differs');}
 else fs.writeFileSync(dest,frozen);
}
console.log('Eight original input PNGs and both case snapshots match their frozen manifests.');
