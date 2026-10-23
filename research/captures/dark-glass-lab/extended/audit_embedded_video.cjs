const fs=require('fs'),cp=require('child_process'),crypto=require('crypto'),path=require('path');
const repo='/workspace/research-docs-publish',audit='/evidence/dark-glass-lab/extended/video-metadata-audit';
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const source=cp.execFileSync('git',['rev-parse','HEAD'],{cwd:repo,encoding:'utf8'}).trim(),items=[];
for(const id of ['music-mini-expanded-vector','music-mini-compact-vector','music-search-vector','music-home-vector'])for(const sample of ['a','b'])items.push({id,sample,asset:'docs/liquid-glass/assets/study-'+id+'-paired-'+sample+'.mp4',manifest:'docs/liquid-glass/experiments/reconstruction/studies/'+id+'/paired/'+sample+'/media.json'});
items.push({id:'playback',sample:'settled',asset:'docs/liquid-glass/assets/playback-settled.mp4',manifest:null});
const records=[];fs.mkdirSync(audit,{recursive:true});
for(const item of items){
 const folder=path.join(audit,item.id,item.sample);fs.mkdirSync(folder,{recursive:true});
 if(fs.existsSync(folder+'/result.json'))throw Error('Preserve prior completed audit; inspect before rerunning '+item.id+'/'+item.sample);
 const digest=sha(path.join(repo,item.asset));fs.copyFileSync(path.join(repo,item.asset),folder+'/motion.mp4');
 const render={render_files:{'motion.mp4':digest},audit_input:{git_commit:source,asset:item.asset,manifest:item.manifest,manifest_sha256:item.manifest?sha(path.join(repo,item.manifest)):null}};
 fs.writeFileSync(folder+'/render.json',JSON.stringify(render,null,2)+'\n');
 const verification=item.manifest?JSON.parse(fs.readFileSync(path.join(repo,item.manifest))):{files:{'motion.mp4':{bytes:fs.statSync(folder+'/motion.mp4').size,sha256:digest}}};
 if(verification.files['motion.mp4'].sha256!==digest)throw Error('Public manifest mismatch '+item.asset);
 verification.render_files??={};verification.render_files['motion.mp4']=digest;
 fs.writeFileSync(folder+'/verification.json',JSON.stringify(verification,null,2)+'\n');
 const dockerFolder='/evidence/extended/video-metadata-audit/'+item.id+'/'+item.sample;
 const raw=cp.execFileSync('docker',['exec','-e','PYTHONPATH=/tmp/optics-deps:/tmp/optics-fit-deps','glass-research','sh','-c','umask 0002; exec "$@"','sh','python3','/workspace/docs/liquid-glass/experiments/reconstruction/video_color.py',dockerFolder],{cwd:repo,encoding:'utf8',env:{...process.env,LC_ALL:'C'},maxBuffer:1024*1024});
 const result=JSON.parse(raw);fs.writeFileSync(folder+'/result.json',JSON.stringify({...item,source,result},null,2)+'\n');
 if(sha(path.join(repo,item.asset))!==digest)throw Error('Public video changed during audit');
 if(!result.already_declared){
  if(result.equal_decoded_rgb!==true)throw Error('No decoded-RGB equality evidence');
  fs.copyFileSync(folder+'/motion.mp4',path.join(repo,item.asset));
  if(item.manifest)fs.copyFileSync(folder+'/verification.json',path.join(repo,item.manifest));
  else fs.writeFileSync(path.join(repo,'docs/liquid-glass/experiments/reconstruction/playback-video-color.json'),JSON.stringify({input:render.audit_input,...result},null,2)+'\n');
 }
 records.push({...item,result});fs.writeFileSync(audit+'/report.json',JSON.stringify({source,records},null,2)+'\n');
 for(const p of [folder,path.join(repo,item.asset),...(item.manifest?[path.join(repo,item.manifest)]:[path.join(repo,'docs/liquid-glass/experiments/reconstruction/playback-video-color.json')])])cp.execFileSync('/workspace/fix-permissions.sh',[p],{env:{...process.env,LC_ALL:'C'}});
 console.log(JSON.stringify({id:item.id,sample:item.sample,equal_decoded_rgb:result.equal_decoded_rgb,already_declared:result.already_declared}));
}
