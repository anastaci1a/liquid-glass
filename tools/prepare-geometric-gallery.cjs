// Restore declared saved image inputs; leave scientific source artifacts intact.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),cp=require('child_process');
const root=path.resolve(__dirname,'..'),base=path.join(root,'.evidence-working/geometric-gallery');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'research/presentation/geometric-gallery-inputs.json')));
fs.mkdirSync(base,{recursive:true});
for(const record of manifest.artifacts){
 const file=path.join(base,record.id+path.extname(record.logical));
 if(fs.existsSync(file)){
  if(crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')!==record.sha256)throw Error('Different local artifact');
  continue;
 }
 const bytes=cp.execFileSync('zstd',['-q','-d','-c','--',path.join(root,record.object)],{maxBuffer:record.bytes+1048576});
 if(bytes.length!==record.bytes||crypto.createHash('sha256').update(bytes).digest('hex')!==record.sha256)throw Error('Invalid artifact');
 fs.writeFileSync(file,bytes,{flag:'wx'});
}
console.log('Verified '+manifest.artifacts.length+' saved gallery inputs.');
