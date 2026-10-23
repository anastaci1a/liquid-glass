const fs=require('fs'),cp=require('child_process'),path=require('path');
const id=process.argv[2];if(!/^[a-z0-9-]+$/.test(id||''))throw Error('Need study ID');
const repo='/workspace/research-docs-publish',root=repo+'/../evidence/dark-glass-lab/extended',base=root+'/'+id,dest=base+'/paired',inputs=root+'/'+id+'-inputs';
if(fs.existsSync(dest)||fs.existsSync(inputs))throw Error('Preserve existing pair/input sets');
const records=fs.readdirSync(base).filter(f=>/^pass-\d+$/.test(f)&&fs.existsSync(base+'/'+f+'/record.json'));
if(records.length<20)throw Error('Need20 initial experiments first');
fs.mkdirSync(dest);fs.mkdirSync(inputs);const first=JSON.parse(fs.readFileSync(base+'/case.json'));
for(const name of ['a','b']){
 const source=name==='a'?base:base+'/second-observation',out=dest+'/'+name;fs.mkdirSync(out);const c=JSON.parse(fs.readFileSync(source+'/case.json'));c.id=id+'-'+name;
 if(Math.abs(c.parameter_length_reference-first.parameter_length_reference)>1e-12)throw Error('Shared kernel basis differs');
 for(const file of Object.keys(c.source_sha256)){fs.copyFileSync(source+'/'+file,out+'/'+file);const flat=c.input_names[file];if(!flat)throw Error('Undeclared input '+file);fs.copyFileSync(source+'/'+file,inputs+'/'+flat);}
 for(const layer of c.foreground_layers)for(const key of ['vector_asset','artwork_asset'])if(layer[key]){fs.copyFileSync(source+'/'+layer[key],out+'/'+layer[key]);fs.copyFileSync(source+'/'+layer[key],inputs+'/'+layer[key]);}
 fs.writeFileSync(out+'/case.json',JSON.stringify(c,null,2)+'\n');
}
fs.copyFileSync(base+'/accepted.json',dest+'/initial.json');
cp.execFileSync(repo+'/../fix-permissions.sh',[dest,inputs],{stdio:'inherit'});
console.log('Prepared shared-model pair; initial parameters/material unchanged. First nativeA boundary still requires independent verification.');
