const fs=require('fs'),path=require('path'),cp=require('child_process'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..'),base=path.join(root,'.evidence-working/expanded-geometry-02');
const index=JSON.parse(fs.readFileSync(path.join(root,'research/evidence/index.json'))).logical_files;
const capture=path.join(root,'research/captures/dark-glass-lab/extended/agent-pipeline-01');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');const records=[];
function write(file,bytes){if(fs.existsSync(file)&&sha(fs.readFileSync(file))!==sha(bytes))throw Error('Different existing input');fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,bytes);}
function restore(r,file){if(!r?.object)throw Error('Missing indexed artifact');if(fs.existsSync(file)){if(sha(fs.readFileSync(file))!==r.sha256)throw Error('Different restored bytes');records.push({logical:r.logical,sha256:r.sha256,bytes:r.bytes});return;}const data=cp.execFileSync('zstd',['-q','-d','-c','--',path.join(root,r.object)],{maxBuffer:r.bytes+1048576});if(data.length!==r.bytes||sha(data)!==r.sha256)throw Error('Digest mismatch');write(file,data);records.push({logical:r.logical,sha256:r.sha256,bytes:r.bytes});}
for(const k of ['a','b']){
 const b=fs.readFileSync(path.join(capture,'inputs',k,'case.json')),c=JSON.parse(b);write(path.join(base,k,'case.json'),b);
 const inputs={...c.source_sha256};for(const l of c.foreground_layers){if(l.vector_asset)inputs[l.vector_asset]=l.vector_sha256;if(l.artwork_asset)inputs[l.artwork_asset]=l.artwork_sha256;}
 for(const [name,digest]of Object.entries(inputs)){if(path.basename(name)!==name)throw Error('Unsafe name');restore(index.find(r=>r.sha256===digest&&r.object),path.join(base,k,name));}
 for(const h of ['h1','h2'])restore(index.find(r=>r.logical===`dark-glass-lab/extended/agent-pipeline-01/refraction/${h}/${k}-native-paths.npz`),path.join(base,`${h}-${k}-paths.npz`));
}
for(const r of JSON.parse(fs.readFileSync(path.join(__dirname,'additional-inputs.json'))).records)restore(index.find(x=>x.logical===r.logical),path.join(base,r.destination));
fs.writeFileSync(path.join(__dirname,'inputs.json'),JSON.stringify({records,cases:'Original committed helper snapshots; no new style/source changes'},null,2)+'\n');console.log('Verified and restored',records.length,'input/path artifacts');
