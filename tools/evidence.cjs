#!/usr/bin/env node
// Restore immutable, hash-verified evidence without old workspace dependencies.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),cp=require('child_process');
const root=path.resolve(__dirname,'..'),index=JSON.parse(fs.readFileSync(path.join(root,'research/evidence/index.json')));
const [command='list',query='',output='']=process.argv.slice(2);
const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
const selected=index.logical_files.filter(r=>r.object&&r.logical.includes(query));
if(command==='list'){for(const r of selected)console.log(r.logical);process.exit(0);}
if(!['verify','restore'].includes(command))throw Error('Use list, verify or restore [logical substring] [output directory]');
if(command==='restore'&&!output)throw Error('An explicit output directory is required');
const seen=new Set();let count=0;
for(const r of selected){if(command==='verify'&&seen.has(r.sha256))continue;seen.add(r.sha256);const source=path.resolve(root,r.object);if(!source.startsWith(root+path.sep))throw Error('Unsafe object path');
 const data=cp.execFileSync('zstd',['-q','-d','-c','--',source],{maxBuffer:Math.max(r.bytes+1048576,64*1024*1024)});if(data.length!==r.bytes||digest(data)!==r.sha256)throw Error('Evidence mismatch: '+r.logical);
 if(command==='restore'){const dest=path.resolve(output,r.logical),base=path.resolve(output);if(!dest.startsWith(base+path.sep))throw Error('Unsafe logical path');fs.mkdirSync(path.dirname(dest),{recursive:true});if(fs.existsSync(dest)&&digest(fs.readFileSync(dest))!==r.sha256)throw Error('Refusing to overwrite different bytes: '+dest);fs.writeFileSync(dest,data);}
 count++;
}
console.log(command+': '+count+' verified objects/files');
