const cp=require('child_process'),fs=require('fs');const[id,begin='1',end='20']=process.argv.slice(2);if(!id)throw Error('Need study');
const root='/mnt/user/live/projects/localica/localica-feedback/dark-glass-lab/extended',cwd='/mnt/user/live/projects/localica/localica-docs-publish';
for(let n=+begin;n<=+end;n++){
 cp.execFileSync('docker',['exec','-e','PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps','-e','OPENBLAS_NUM_THREADS=1','localica-dark-lab-check','sh','-c','umask 0002; exec "$@"','sh','python3','/workspace/docs/liquid-glass/experiments/reconstruction/paired_fit.py','/evidence/extended/'+(id==='music-home-vector'?'music-home-vector-corrected':id)+'/paired','--pass',String(n)],{cwd,stdio:'inherit',env:{...process.env,LC_ALL:'C'}});
 cp.execFileSync('node',[root+'/paired_checkpoint.cjs',id,String(n)],{cwd,stdio:'inherit',env:{...process.env,LC_ALL:'C'}});
}
