const cp=require('child_process'),fs=require('fs');
const base='/evidence/dark-glass-lab/extended/active-switch-paired-replay';
for(const sample of ['a','b']){
 const log=fs.openSync(base+'/'+sample+'/media.log','w');console.log('Rendering switch '+sample+' at4x');
 cp.execFileSync('docker',['exec','-e','PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps','-e','OPENBLAS_NUM_THREADS=1','glass-research','sh','-c','umask 0002; exec "$@"','sh','python3','/workspace/docs/liquid-glass/experiments/reconstruction/extended_media.py','/evidence/extended/active-switch-paired-replay/'+sample],{stdio:['ignore',log,log],env:{...process.env,LC_ALL:'C'}});fs.closeSync(log);
 console.log('Completed '+sample);cp.execFileSync('/workspace/fix-permissions.sh',[base+'/'+sample]);
}
