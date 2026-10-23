// Three-way merge of independent figure metadata; reject conflicting edits.
const fs=require('fs'),cp=require('child_process'),root=process.argv[2],p='docs/liquid-glass/comparison-panels.json';const read=n=>JSON.parse(cp.execFileSync('git',['-C',root,'show',':'+n+':'+p]));const base=read(1),ours=read(2),theirs=read(3),same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
for(const k of new Set([...Object.keys(base),...Object.keys(theirs)])){
 if(same(base[k],theirs[k]))continue;
 if(!theirs[k]){if(!same(base[k],ours[k]))throw Error('Conflicting removal: '+k);delete ours[k];continue;}
 ours[k]??={};for(const prop of new Set([...Object.keys(base[k]||{}),...Object.keys(theirs[k])])){
  const a=base[k]?.[prop],o=ours[k][prop],t=theirs[k][prop];if(same(a,t))continue;if(!same(a,o)&&!same(o,t))throw Error('Conflicting value: '+k+'.'+prop);
  if(t===undefined)delete ours[k][prop];else ours[k][prop]=t;
 }
}
fs.writeFileSync(root+'/'+p,JSON.stringify(ours,null,2)+'\n');
