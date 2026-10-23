const fs=require('fs'),path=require('path'),crypto=require('crypto');const root='/evidence/dark-glass-lab/extended';const[id,sourceName='music-recovery',seconds='6.0']=process.argv.slice(2);if(!id)throw Error('Need study');const base=root+'/'+id,dest=base+'/paired';if(fs.existsSync(dest))throw Error('Do not replace frozen pair');fs.mkdirSync(dest);
const config=JSON.parse(fs.readFileSync(base+'/case.json')),input=root+'/'+sourceName,recovery=JSON.parse(fs.readFileSync(input+'/recovery.json'));const requested=Number(seconds),decoded=recovery.timestamps.reduce((a,b)=>Math.abs(a-requested)<Math.abs(b-requested)?a:b);
for(const name of ['a','b']){
 const c=structuredClone(config);c.id=id+'-'+name;const d=dest+'/'+name;fs.mkdirSync(d);
 if(name==='b'){c.reference={...c.reference,seconds:decoded,requested_seconds:requested};c.input_names={};c.source_sha256={};}
 for(const file of ['source.png','target.png','known.png']){
  const src=name==='a'?base+'/'+file:input+'/'+file.replace('.png','-'+seconds+'.png');fs.linkSync(src,d+'/'+file);
  if(name==='b'){c.input_names[file]=file.replace('.png','-'+seconds+'.png');c.source_sha256[file]=crypto.createHash('sha256').update(fs.readFileSync(src)).digest('hex');}
 }
 for(const layer of c.foreground_layers)for(const key of ['vector_asset','artwork_asset'])if(layer[key])fs.copyFileSync(base+'/'+layer[key],d+'/'+layer[key]);
 fs.writeFileSync(d+'/case.json',JSON.stringify(c,null,2)+'\n');
}
fs.copyFileSync(base+'/accepted.json',dest+'/initial.json');
