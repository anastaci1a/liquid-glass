const fs=require('fs'),path=require('path');
const root='/mnt/user/live/projects/localica/localica-feedback/dark-glass-lab/extended/active-switch',out=root+'/paired';
if(fs.existsSync(out))throw Error('Preserve frozen pair');fs.mkdirSync(out);
for(const name of ['a','b']){
 const src=name==='a'?root:root+'/second-observation',dest=out+'/'+name;fs.mkdirSync(dest);
 const c=JSON.parse(fs.readFileSync(src+'/case.json'));c.id='active-switch-'+name;
 c.signed_normal_profile=true;c.allow_center_reduction=true;
 for(const file of Object.keys(c.source_sha256))fs.linkSync(src+'/'+file,dest+'/'+file);
 fs.writeFileSync(dest+'/case.json',JSON.stringify(c,null,2)+'\n');
}
fs.copyFileSync(root+'/accepted.json',out+'/initial.json');
