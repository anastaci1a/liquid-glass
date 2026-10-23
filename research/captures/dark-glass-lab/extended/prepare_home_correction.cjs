const fs=require('fs'),path=require('path'),cp=require('child_process');
const base='/mnt/user/live/projects/localica/localica-feedback/dark-glass-lab/extended',repo='/mnt/user/live/projects/localica/localica-docs-publish';
const old=base+'/music-home-vector',privateRoot=base+'/music-home-vector-corrected/paired',inputs=base+'/home-corrected-inputs',pub=repo+'/docs/liquid-glass/experiments/reconstruction/studies/music-home-vector',archive=pub+'/paired-invalid-boundary';
if(fs.existsSync(privateRoot)||fs.existsSync(archive))throw Error('Preserve existing correction');
const candidate=JSON.parse(fs.readFileSync(old+'/inset-context-bridge.json')),best=candidate.best,prior=JSON.parse(fs.readFileSync(old+'/paired/accepted.json'));
const verified=JSON.parse(fs.readFileSync(base+'/home-context-final-verification.log','utf8').trim().split('\n').at(-1));
if(!verified.status.startsWith('PASS'))throw Error('Verify candidate first');
const state={parameters:best.parameters,material:best.material,scores:best.scores,foreground_response:prior.foreground_response,foreground_scores:{before_mse:verified.foreground_mse,after_mse:verified.foreground_mse}};
fs.mkdirSync(privateRoot,{recursive:true});fs.mkdirSync(inputs,{recursive:true});
for(const n of ['a','b']){
 const src=old+'/paired/'+n,dest=privateRoot+'/'+n,c=JSON.parse(fs.readFileSync(src+'/case.json'));fs.mkdirSync(dest);
 const names=new Set(Object.keys(c.source_sha256));for(const layer of c.foreground_layers||[])if(layer.vector_asset)names.add(layer.vector_asset);
 for(const name of names){fs.copyFileSync(src+'/'+name,dest+'/'+name);fs.copyFileSync(src+'/'+name,inputs+'/'+(c.input_names[name]||name));}
 c.foreground_response=state.foreground_response;fs.writeFileSync(dest+'/case.json',JSON.stringify(c,null,2)+'\n');
}
for(const name of ['initial.json','baseline.json','accepted.json'])fs.writeFileSync(privateRoot+'/'+name,JSON.stringify(state,null,2)+'\n');
const L=Math.min(...JSON.parse(fs.readFileSync(privateRoot+'/a/case.json')).half),normalized={...state,parameters:{...state.parameters,sigma:state.parameters.sigma/L,post_sigma:state.parameters.post_sigma/L}};
const proof={status:'Verified baseline for a NEW corrected paired chain; old invalid receipts archived unchanged.',code_commit:cp.execFileSync('git',['rev-parse','HEAD'],{cwd:repo,encoding:'utf8'}).trim(),protected_single_loss:candidate.targets[0].loss,protected_old_second_loss:candidate.targets[1].loss,current:normalized,verification:verified,model:candidate.model,history:candidate.history,limits:candidate.limits};
fs.renameSync(pub+'/paired',archive);fs.writeFileSync(archive+'/status.json',JSON.stringify({status:'Historical invalid single-to-paired boundary; not current acceptance',reason:'Initial paired A loss56.108072 exceeded retained single40.344658 with the same frozen reference protocol.',source_commit:'74fd684b97e2dcabdc40a837d5a635891d8a5950',media:'Original raw assets remain in that Git commit; current assets may be replaced by corrected captures.'},null,2)+'\n');
fs.mkdirSync(pub+'/paired');for(const n of ['a','b'])fs.copyFileSync(privateRoot+'/'+n+'/case.json',pub+'/paired/'+n+'.json');
fs.writeFileSync(pub+'/paired/accepted.json',JSON.stringify(normalized,null,2)+'\n');fs.writeFileSync(pub+'/paired/bridge.json',JSON.stringify(proof,null,2)+'\n');
for(const p of [privateRoot,inputs,pub])cp.execFileSync('/mnt/user/live/projects/localica/fix-permissions.sh',[p]);console.log(JSON.stringify({privateRoot,inputs,normalizedLoss:normalized.scores.map(x=>x.loss)}));
