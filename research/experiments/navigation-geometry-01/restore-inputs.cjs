const fs=require('fs'),path=require('path'),cp=require('child_process'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..'),base=path.join(root,'.evidence-working/navigation-geometry-01');
const index=JSON.parse(fs.readFileSync(path.join(root,'research/evidence/index.json')));
const source=path.join(root,'research/captures/dark-glass-lab/extended/helper-toolbar-work/navigation-round/short-outer-profile');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function write(file,bytes){if(fs.existsSync(file)&&sha(fs.readFileSync(file))!==sha(bytes))throw Error('Refusing different local input');fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,bytes);}
for(const k of ['a','b']){
 const bytes=fs.readFileSync(path.join(source,k,'case.json')),c=JSON.parse(bytes),folder=path.join(base,k);
 write(path.join(folder,'case.json'),bytes);
 const inputs={...c.source_sha256};for(const layer of c.foreground_layers)inputs[layer.vector_asset]=layer.vector_sha256;
 for(const [name,digest] of Object.entries(inputs)){
  if(path.basename(name)!==name)throw Error('Unsafe input filename');
  const record=index.logical_files.find(r=>r.sha256===digest&&r.object);if(!record)throw Error('Missing indexed input');
  const data=cp.execFileSync('zstd',['-q','-d','-c','--',path.join(root,record.object)],{maxBuffer:Math.max(record.bytes+1048576,8*1024*1024)});
  if(data.length!==record.bytes||sha(data)!==digest)throw Error('Input digest mismatch');write(path.join(folder,name),data);
 }
}
console.log('Both reference inputs and vectors restored and verified.');
