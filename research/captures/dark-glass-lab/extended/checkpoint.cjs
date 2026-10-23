// Run on the host after a completed pass. Private inputs never enter Git.
const fs=require('fs'),path=require('path'),cp=require('child_process'),crypto=require('crypto');
const [id,number]=process.argv.slice(2),root='/evidence/dark-glass-lab/extended';
const repo='/workspace/research-docs-publish';
if(!id||!number)throw Error('Usage: checkpoint.cjs element pass');
const input=path.join(root,id),dest=path.join(repo,'docs/liquid-glass/experiments/reconstruction/studies',id);
const record=JSON.parse(fs.readFileSync(path.join(input,`pass-${number.padStart(2,'0')}/record.json`)));
const config=JSON.parse(fs.readFileSync(path.join(input,'case.json'))),L=Math.min(...config.half);
const normalize=p=>({...p,sigma:p.sigma/L,post_sigma:p.post_sigma/L});
const row={pass:record.pass_number,experiment:record.experiment,evaluations:record.evaluations,
 accepted:record.accepted,previous:record.incumbent_scores,trial:record.candidate.scores,retained:record.current.scores,
 trial_parameters:normalize(record.candidate.parameters),retained_parameters:normalize(record.current.parameters),
 material:record.current.material,gate:record.gate,
 execution_script:record.execution_script||'extended_fit.py',
 code_sha256:record.code_sha256||crypto.createHash('sha256').update(fs.readFileSync(path.join(repo,'docs/liquid-glass/experiments/reconstruction/extended_fit.py'))).digest('hex')};
fs.mkdirSync(dest,{recursive:true});fs.writeFileSync(path.join(dest,'case.json'),JSON.stringify(config,null,2)+'\n');
const log=path.join(dest,'passes.jsonl');let rows=fs.existsSync(log)?fs.readFileSync(log,'utf8').trim().split('\n').filter(Boolean).map(JSON.parse):[];
if(rows.some(r=>r.pass===row.pass))throw Error('Immutable public pass already recorded');
rows.push(row);rows.sort((a,b)=>a.pass-b.pass);fs.writeFileSync(log,rows.map(JSON.stringify).join('\n')+'\n');
fs.writeFileSync(path.join(dest,'accepted.json'),JSON.stringify({units:'All lengths, including sigma/post_sigma, are normalized by L=min(half extents). Reference pose is separate.',shape:{half:config.half.map(v=>v/L),radius:config.radius/L},parameters:normalize(record.current.parameters),material:record.current.material,scores:record.current.scores,pass:row.pass},null,2)+'\n');
let progress=JSON.parse(fs.readFileSync(path.join(root,'progress.json')));progress.completed[id]=rows.map(r=>r.pass);fs.writeFileSync(path.join(root,'progress.json'),JSON.stringify(progress,null,2)+'\n');
for(let p of [dest,path.join(repo,'docs/liquid-glass/experiments/reconstruction/extended_fit.py'),input,path.join(root,'progress.json')])cp.execFileSync('/workspace/fix-permissions.sh',[p],{stdio:'ignore'});
const git=args=>cp.execFileSync('git',args,{cwd:repo,stdio:'inherit'});
git(['add',...['extended_fit.py','extended_shadow.py','extended_media.py','extended_replay.py','extended_verify.py','extended_diagnostics.py','foreground_response.py'].filter(f=>fs.existsSync(path.join(repo,'docs/liquid-glass/experiments/reconstruction',f))).map(f=>'docs/liquid-glass/experiments/reconstruction/'+f),path.relative(repo,dest)]);
if(id==='active-segmented-selector'){
 cp.execFileSync('docker',['exec','-e','OPENBLAS_NUM_THREADS=1','-e','PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps','glass-research','sh','-c','umask 0002; exec "$@"','sh','python3','/workspace/docs/liquid-glass/experiments/reconstruction/single_gallery.py','/evidence/extended/'+id,'--id',id,'--pass',number,'--code-commit',cp.execFileSync('git',['rev-parse','HEAD'],{cwd:repo,encoding:'utf8'}).trim()],{cwd:repo,stdio:'inherit'});
 const files=['docs/liquid-glass/reconstruction.md','docs/liquid-glass/experiments/reconstruction/single_gallery.py','docs/liquid-glass/experiments/reconstruction/comparison.cjs','docs/liquid-glass/experiments/reconstruction/'+id+'-progress.json','docs/liquid-glass/assets/study-'+id+'-progress-a.png'];
 cp.execFileSync('/workspace/fix-permissions.sh',files.map(f=>repo+'/'+f));git(['add',...files]);
}
git(['diff','--cached','--check']);git(['commit','-m',`Refine ${id} pass ${String(row.pass).padStart(2,'0')}: ${record.experiment.toLowerCase()} (#222) [skip ci]`]);
git(['push','-u','origin','HEAD']);

if(id==='active-segmented-selector')cp.execFileSync('node',[root+'/publish_checkpoint.cjs'],{cwd:repo,stdio:'inherit'});

if(fs.existsSync(root+'/pause-after-single'))process.exit(75);
