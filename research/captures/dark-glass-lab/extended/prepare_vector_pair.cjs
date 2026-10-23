const fs=require('fs'),path=require('path');const root='/evidence/dark-glass-lab/extended';
const id=process.argv[2]||'music-home-vector',base=path.join(root,id),old=path.join(root,id.replace('-vector',''));
const dest=path.join(base,'paired');fs.mkdirSync(dest,{recursive:true});if(fs.existsSync(path.join(dest,'initial.json')))throw Error('Do not replace a frozen pair');
const config=JSON.parse(fs.readFileSync(path.join(base,'case.json')));
for(const name of ['a','b']){
 const target=path.join(dest,name);fs.mkdirSync(target,{recursive:true});
 const c=JSON.parse(fs.readFileSync(path.join(old,'paired',name,'case.json')));c.id=id+'-'+name;c.foreground_layers=config.foreground_layers;c.foreground_method=config.foreground_method;c.foreground_provenance=config.foreground_provenance;c.foreground_response=config.foreground_response;c.continuation=config.continuation;
 for(const f of ['source.png','target.png','known.png'])fs.linkSync(path.join(old,'paired',name,f),path.join(target,f));
 for(const layer of c.foreground_layers)if(layer.vector_asset)fs.copyFileSync(path.join(base,layer.vector_asset),path.join(target,layer.vector_asset));
 fs.writeFileSync(path.join(target,'case.json'),JSON.stringify(c,null,2)+'\n');
}
fs.copyFileSync(path.join(base,'accepted.json'),path.join(dest,'initial.json'));
