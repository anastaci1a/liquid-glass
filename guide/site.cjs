// Public research documentation, historical reports and illustrative Lab.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {execFileSync}=require('node:child_process');
const {zstdDecompressSync}=require('node:zlib');
const {prepareMedia}=require('./guide-media.cjs');
const {prepareStudies}=require('./guide-studies.cjs');
const project=path.resolve(__dirname,'..'),guide=__dirname,lab=path.join(project,'lab');
const sha=data=>crypto.createHash('sha256').update(data).digest('hex');
const escape=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
const slug=s=>s.replace(/<[^>]*>/g,'').toLowerCase().replace(/[^\p{L}\p{N}\s-]/gu,'').replace(/\s/g,'-');
const normalize=s=>path.posix.normalize(s).replace(/^historical-records\//,'');
(async()=>{
  const {Marked}=await import('marked'),katex=require('katex');
  const out=path.resolve(process.argv[2]||path.join(guide,'site'));
  fs.mkdirSync(out,{recursive:true});
  const previous=fs.existsSync(path.join(out,'build.json'))?JSON.parse(fs.readFileSync(path.join(out,'build.json'),'utf8')):{files:{}};
  const source=execFileSync('git',['rev-parse','HEAD'],{cwd:project,encoding:'utf8'}).trim();
  const manifest={source,files:{},documentation:[]};
  function write(file,data){
    const target=path.resolve(out,file);
    if(!target.startsWith(out+path.sep))throw Error('Unsafe output path: '+file);
    if(file.endsWith('.html'))data=data.toString().replace(/(href|src)="((?!https?:|data:)[^"?]+\.(?:js|css|png|gif|svg|webp|mp4))"/g,(_,attr,url)=>`${attr}="${url}?v=${source.slice(0,12)}"`);
    fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,data);manifest.files[file]=sha(data);
  }
  const tracked=execFileSync('git',['ls-files','--cached','--others','--exclude-standard','-z'],{cwd:project,encoding:'utf8',maxBuffer:32e6}).split('\0').filter(f=>f&&fs.existsSync(path.join(project,f)));
  const docs=tracked.filter(f=>f.endsWith('.md')&&!f.startsWith('research/captures/'));
  function route(file){
    if(file==='README.md')return 'research.html';
    if(file==='lab/README.md')return 'lab-guide.html';
    if(file.startsWith('guide/'))return file.slice(6).replace(/README\.md$/,'index.html').replace(/\.md$/,'.html');
    return file.replace(/README\.md$/,'index.html').replace(/\.md$/,'.html');
  }
  const routes=new Map(docs.map(f=>[f,route(f)]));
  const index=JSON.parse(fs.readFileSync(path.join(project,'research/evidence/index.json')));
  const library=new Map(index.logical_files.filter(r=>r.object).map(r=>[normalize(r.logical),r]));
  const reports=[...library].filter(([name])=>name.endsWith('.md'));
  const reportRoute=name=>'records/'+sha(name).slice(0,20)+'.html';
  const artifactRoute=r=>'artifacts/'+r.sha256+'.html';
  const relative=(from,to)=>path.posix.relative(path.posix.dirname(from),to)||path.posix.basename(to);
  function shell(output,title,body){
    const local=p=>relative(output,p);
    return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escape(title)} · Liquid Glass</title><link rel="stylesheet" href="${local('lab.css')}"><link rel="stylesheet" href="${local('guide.css')}"><link rel="stylesheet" href="${local('katex/katex.min.css')}"></head><body class="guide"><script src="${local('guide-media.js')}" defer></script><script src="${local('guide-comparison.js')}" defer></script><nav aria-label="Research"><a href="${local('index.html')}">Research</a><a href="${local('reconstruction.html')}">Comparisons</a><a href="${local('research/evidence/catalogue.html')}">Reports</a><a href="${local('lab.html')}">Lab</a></nav><main>${body}</main><footer>Mathematical models and reference evidence · <a href="https://github.com/anastaci1a/liquid-glass/tree/${source}">Source ${source.slice(0,8)}</a> · No claim of access to Apple's private renderer.</footer></body></html>`;
  }
  function targetForFile(file){
    if(routes.has(file))return routes.get(file);
    if(file==='lab/index.html')return 'lab.html';
    if(/^lab\/(lab|software|model)\.js$/.test(file))return path.posix.basename(file);
    if(file==='LICENSE')return 'license.txt';
    if(file.startsWith('reconstruction/'))return 'experiments/'+file;
    if(file.startsWith('guide/'))return file.slice(6);
    if(tracked.includes(file)&&fs.statSync(path.join(project,file)).isFile()){const destination='source/'+file;write(destination,fs.readFileSync(path.join(project,file)));return destination;}
    return null;
  }
  function renderer(file,output,archival=false){
    function link(href){
      if(!href||/^(#|mailto:|data:)/.test(href))return href;
      const hosted=/^https:\/\/(?:github.com\/anastaci1a\/liquid-glass\/blob\/[^/]+\/|raw.githubusercontent.com\/anastaci1a\/liquid-glass\/[^/]+\/)([^#]+\.md)(#.*)?$/.exec(href);
      if(hosted&&routes.has(hosted[1]))return relative(output,routes.get(hosted[1]))+(hosted[2]||'');
      if(/^https?:/.test(href))return href;
      const [name,fragment]=href.split('#');
      if(!name)return href;
      const resolved=path.posix.normalize(path.posix.join(path.posix.dirname(file),name));
      if(archival){
        const key=normalize(resolved),record=library.get(key);
        if(record)return relative(output,key.endsWith('.md')?reportRoute(key):artifactRoute(record))+(key.endsWith('.md')&&fragment?'#'+fragment:'');
        return null; // Unavailable historical file references stay labeled text.
      }
      const destination=targetForFile(resolved);
      if(!destination)throw Error(file+': no website route for '+href);
      return relative(output,destination)+(fragment?'#'+fragment:'');
    }
    const md=new Marked({extensions:[{name:'displayMath',level:'block',start(src){return src.indexOf('$$');},tokenizer(src){const m=/^\$\$\n([\s\S]*?)\n\$\$(?:\n|$)/.exec(src);if(m)return {type:'displayMath',raw:m[0],text:m[1]};},renderer(token){return '<div class="display-math">'+katex.renderToString(token.text,{displayMode:true,throwOnError:true,strict:'error',trust:false})+'</div>\n';}}],renderer:{
      heading({tokens,depth}){const text=this.parser.parseInline(tokens);return `<h${depth} id="${slug(text)}">${text}</h${depth}>\n`;},
      link({href,title,tokens}){const target=link(href),label=this.parser.parseInline(tokens);return target?`<a href="${escape(target)}"${title?` title="${escape(title)}"`:''}>${label}</a>`:`<span title="Historical reference not included in this record">${label}</span>`;},
      html(token){if(!archival)return false;return '<pre class="record-markup">'+escape(token.text)+'</pre>';},
      image(token){const target=link(token.href);if(!archival)return `<img src="${escape(target)}" alt="${escape(token.text)}"${token.title?` title="${escape(token.title)}"`:""}>`;return target?`<a href="${escape(target)}">Figure evidence: ${escape(token.text)}</a>`:`<span>Figure reference: ${escape(token.text)}</span>`;}
    }});
    return md;
  }
  for(const file of docs){
    const output=routes.get(file),markdown=fs.readFileSync(path.join(project,file),'utf8');
    let content=renderer(file,output).parse(markdown);
    if(file==='research/evidence/catalogue.md'){
      const groups=new Map();for(const [name,r]of reports){const group=path.posix.dirname(name);if(!groups.has(group))groups.set(group,[]);groups.get(group).push({name,r});}
      content+=[...groups].sort(([a],[b])=>a.localeCompare(b)).map(([group,items])=>`<details class="report-group"><summary>${escape(group)} (${items.length})</summary><ul>${items.map(({name})=>`<li><a href="${relative(output,reportRoute(name))}">${escape(path.posix.basename(name))}</a></li>`).join('')}</ul></details>`).join('\n');
    }
    if(file==='guide/reconstruction.md')content=await prepareStudies(content,guide,write);
    if(file.startsWith('guide/'))content=prepareMedia(content,guide,{comparisons:['guide/reconstruction.md','guide/outline-review.md','guide/miniplayer-refinement.md','guide/miniplayer-feedback-review.md','guide/miniplayer-middle-ground.md','guide/miniplayer-four-pass.md','guide/miniplayer-three-pass.md','guide/miniplayer-hsv-options.md','guide/miniplayer-anchor-colors.md','guide/miniplayer-restored-grade.md'].includes(file),panelFile:file==='guide/miniplayer-restored-grade.md'?'restored-grade-comparison-panels.json':file==='guide/miniplayer-anchor-colors.md'?'anchor-color-comparison-panels.json':file==='guide/miniplayer-hsv-options.md'?'hsv-comparison-panels.json':file==='guide/miniplayer-three-pass.md'?'three-pass-comparison-panels.json':file==='guide/miniplayer-four-pass.md'?'four-pass-comparison-panels.json':file==='guide/miniplayer-middle-ground.md'?'middle-ground-comparison-panels.json':file==='guide/miniplayer-feedback-review.md'?'feedback-comparison-panels.json':file==='guide/miniplayer-refinement.md'?'refinement-comparison-panels.json':file==='guide/outline-review.md'?'outline-comparison-panels.json':'comparison-panels.json'});
    const title=(/^#\s+(.+)$/m.exec(markdown)||[])[1]||file;
    write(output,shell(output,title,content));manifest.documentation.push({source:file,route:output});
  }
  // Historical text is read from ordinary Git objects; no large arrays enter Pages.
  for(const [name,r]of reports){
    const data=zstdDecompressSync(fs.readFileSync(path.join(project,r.object)));
    if(data.length!==r.bytes||sha(data)!==r.sha256)throw Error('Report digest mismatch: '+name);
    const output=reportRoute(name),markdown=data.toString('utf8');
    let content=renderer(name,output,true).parse(markdown);
    write(output,shell(output,path.posix.basename(name),`<p class="record-status">Historical scientific record. Original acceptance scope and limitations apply; administrative attribution is normalized.</p><p><a href="${relative(output,artifactRoute(r))}">Evidence identity and download</a></p>${content}`));
  }
  for(const r of index.objects){
    const output=artifactRoute(r),download='https://media.githubusercontent.com/media/anastaci1a/liquid-glass/main/'+r.object;
    const aliases=index.logical_files.filter(x=>x.sha256===r.sha256).map(x=>x.logical);
    write(output,shell(output,'Evidence '+r.sha256.slice(0,12),`<h1>Evidence artifact</h1><p>This is a compressed reproducibility artifact, not a rendered document.</p><dl><dt>Decompressed SHA-256</dt><dd><code>${r.sha256}</code></dd><dt>Bytes</dt><dd>${r.bytes}</dd></dl><ul>${aliases.map(a=>`<li>${escape(a)}</li>`).join('')}</ul><p><a href="${download}">Download Zstandard artifact</a> · <a href="${relative(output,'research/evidence/index.html')}">Restoration instructions</a></p>`));
  }
  for(const name of ['guide.css','guide-media.js','guide-comparison.js','comparison-panels.json'])write(name,fs.readFileSync(path.join(guide,name)));
  for(const name of ['lab.js','software.js','model.js','lab.css'])write(name,fs.readFileSync(path.join(lab,name)));
  write('lab.html',fs.readFileSync(path.join(lab,'index.html')));
  write('license.txt',fs.readFileSync(path.join(project,'LICENSE')));
  for(const name of fs.readdirSync(path.join(guide,'assets')))if(/\.(png|gif|svg|mp4)$/.test(name))write('assets/'+name,fs.readFileSync(path.join(guide,'assets',name)));
  for(const file of tracked)if(file.startsWith('reconstruction/')&&/\.(py|json|jsonl|png|txt|svg)$/.test(file))write('experiments/'+file,fs.readFileSync(path.join(project,file)));
  for(const name of ['reference_patch.py','context-sources.json','model-fixtures.json'])write('experiments/'+name,fs.readFileSync(path.join(guide,'experiments',name)));
  const mathRoot=path.join(project,'node_modules/katex/dist');
  write('katex/katex.min.css',fs.readFileSync(path.join(mathRoot,'katex.min.css')));
  write('katex/LICENSE',fs.readFileSync(path.join(project,'node_modules/katex/LICENSE')));
  for(const name of fs.readdirSync(path.join(mathRoot,'fonts')))write('katex/fonts/'+name,fs.readFileSync(path.join(mathRoot,'fonts',name)));
  write('.nojekyll','');
  for(const name of Object.keys(previous.files||{}))if(!(name in manifest.files)){
    const file=path.resolve(out,name);if(!file.startsWith(out+path.sep))throw Error('Unsafe previous manifest path');
    if(fs.existsSync(file)&&fs.statSync(file).isFile())fs.unlinkSync(file);
  }
  // Normalize stale historical fragments to the surviving report page.
  for(const file of Object.keys(manifest.files).filter(f=>f.startsWith('records/')&&f.endsWith('.html'))){
    const full=path.join(out,file),html=fs.readFileSync(full,'utf8');
    const repaired=html.replace(/href="([^"#]*)#([^"\s]+)"/g,(all,base,fragment)=>{if(/^https?:/.test(base))return all;const target=path.resolve(path.dirname(full),base||path.basename(full));if(fs.existsSync(target)&&!fs.readFileSync(target,'utf8').includes('id="'+fragment+'"'))return 'href="'+(base||path.basename(full))+'"';return all;});
    if(repaired!==html)write(file,repaired);
  }
  fs.writeFileSync(path.join(out,'build.json'),JSON.stringify(manifest,null,2)+'\n');
  console.log(`Built ${Object.keys(manifest.files).length} public files; ${docs.length} maintained documents and ${reports.length} historical reports`);
})().catch(e=>{console.error(e);process.exit(1)});
