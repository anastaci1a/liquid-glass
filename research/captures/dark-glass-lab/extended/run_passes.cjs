// Sequential experiments on ONE element; checkpoint and push every completed pass.
const cp=require('child_process');
const [id,begin,end]=process.argv.slice(2),root='/mnt/user/live/projects/localica/localica-feedback/dark-glass-lab/extended';
const cwd='/mnt/user/live/projects/localica/localica-docs-publish';
if(!id||!begin||!end)throw Error('Usage: run_passes.cjs element first last');
const budgets={1:1800,2:2600,3:3200,4:2200,5:2200,6:2400,7:2200,8:2200,9:2200,10:3600,11:3000,13:2800,14:5000,15:2600,16:3000,17:5000};
for(let n=+begin;n<=+end;n++){
 const script=n===12?'extended_shadow.py':'extended_fit.py';
 const args=['exec','-e','PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps','-e','OPENBLAS_NUM_THREADS=1','localica-dark-lab-check','sh','-c','umask 0002; exec "$@"','sh','python3','/workspace/docs/liquid-glass/experiments/reconstruction/'+script,'/evidence/extended/'+id];
 if(n!==12)args.push('--pass',String(n),'--budget',String(budgets[n]||2200));
 cp.execFileSync('docker',args,{cwd,stdio:'inherit',env:{...process.env,LC_ALL:'C'}});
 cp.execFileSync('node',[root+'/checkpoint.cjs',id,String(n)],{cwd,stdio:'inherit',env:{...process.env,LC_ALL:'C'}});
}
