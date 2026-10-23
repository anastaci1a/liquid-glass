const fs=require('fs'),cp=require('child_process'),crypto=require('crypto'),path=require('path');
const repo='/workspace/research-docs-publish',pages='/workspace/research-tools/recreation-pages-publish';
const run=(c,a,cwd=repo)=>cp.execFileSync(c,a,{cwd,env:{...process.env,LC_ALL:'C'},stdio:'inherit'});
const read=(c,a,cwd=repo)=>cp.execFileSync(c,a,{cwd,env:{...process.env,LC_ALL:'C'},encoding:'utf8'}).trim();
(async()=>{
 if(read('git',['status','--porcelain']))throw Error('Publish a committed clean source tree');
 if(read('git',['status','--porcelain'],pages))throw Error('Preserve dirty Pages worktree');
 const source=read('git',['rev-parse','HEAD']);
 run('node',['docs/liquid-glass/site.cjs']);run('/workspace/fix-permissions.sh',[repo+'/docs/liquid-glass/site']);run('node',['docs/liquid-glass/experiments/check-links.cjs']);
 run('docker',['exec','-e','CHROMIUM_PATH=/browsers/chromium-1248/chrome-linux64/chrome','-e','LAB_EVIDENCE=/evidence/extended/checkpoint-page-qa','glass-research','sh','-c','umask 0002; exec node /workspace/docs/liquid-glass/experiments/reconstruction/page.cjs']);
 run('/workspace/fix-permissions.sh',['/evidence/dark-glass-lab/extended/checkpoint-page-qa']);
 run('git',['fetch','origin','gh-pages'],pages);run('git',['merge','--ff-only','origin/gh-pages'],pages);
 run('node',['docs/liquid-glass/site.cjs',pages]);
 const manifest=JSON.parse(fs.readFileSync(pages+'/build.json'));if(manifest.source!==source)throw Error('Wrong source');
 for(const [name,digest] of Object.entries(manifest.files))if(crypto.createHash('sha256').update(fs.readFileSync(path.join(pages,name))).digest('hex')!==digest)throw Error('Bundle digest mismatch '+name);
 const changed=read('git',['status','--porcelain'],pages);if(changed){run('/workspace/fix-permissions.sh',[pages]);run('git',['add','-A'],pages);run('git',['diff','--cached','--check'],pages);run('git',['commit','-m','Publish recreation checkpoint '+source.slice(0,8)+' [skip ci]'],pages);run('git',['push','origin','HEAD:gh-pages'],pages);}
 const pagesCommit=read('git',['rev-parse','HEAD'],pages),base='https://anastaci1a.github.io/liquid-glass/';
 const changedMedia=read('git',['diff-tree','--no-commit-id','--name-only','-r',pagesCommit],pages).split('\n').filter(n=>n in manifest.files);
 const verify=['liquid-glass/reconstruction.html',...changedMedia];
 let last;
 for(let attempt=0;attempt<36;attempt++){
  try{
   const remote=JSON.parse(cp.execFileSync('curl',['-fsSL',base+'build.json?source='+source],{encoding:'utf8',timeout:20000,maxBuffer:128*1024*1024}));if(remote.source!==source)throw Error('Pages still serves '+remote.source);
   for(const name of verify){const body=cp.execFileSync('curl',['-fsSL',base+name+'?source='+source],{timeout:20000,maxBuffer:128*1024*1024});if(crypto.createHash('sha256').update(body).digest('hex')!==manifest.files[name])throw Error('Stale '+name);}
   const record={source,pagesCommit,verifiedFiles:verify,files:Object.keys(manifest.files).length};fs.writeFileSync('/evidence/dark-glass-lab/extended/latest-checkpoint-deployment.json',JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify(record));return;
  }catch(e){last=e.message;console.log('Waiting for Pages: '+last);await new Promise(r=>setTimeout(r,10000));}
 }
 throw Error('Pushed Pages checkpoint but live verification remains pending: '+last);
})().catch(e=>{console.error(e);process.exit(1)});
