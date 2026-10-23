const fs=require('fs'),path=require('path');const root='/evidence/dark-glass-lab/extended',id=process.argv[2];if(!id)throw Error('Need ID');const base=path.join(root,id),dest=path.join(base,'paired');if(fs.existsSync(dest))throw Error('Do not replace a frozen pair');fs.mkdirSync(dest);
const config=JSON.parse(fs.readFileSync(base+'/case.json'));const second=root+'/music-home/paired/b',other=JSON.parse(fs.readFileSync(second+'/case.json'));
for(const name of ['a','b']){
 const c=structuredClone(config);c.id=id+'-'+name;if(name==='b')for(const k of ['reference','source_sha256','input_names'])c[k]=other[k];
 const d=dest+'/'+name;fs.mkdirSync(d);for(const file of ['source.png','target.png','known.png'])fs.linkSync((name==='a'?base:second)+'/'+file,d+'/'+file);
 for(const layer of c.foreground_layers)if(layer.vector_asset)fs.copyFileSync(base+'/'+layer.vector_asset,d+'/'+layer.vector_asset);
 fs.writeFileSync(d+'/case.json',JSON.stringify(c,null,2)+'\n');
}
fs.copyFileSync(base+'/accepted.json',dest+'/initial.json');
