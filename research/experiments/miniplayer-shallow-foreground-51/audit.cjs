const fs=require('fs'),crypto=require('crypto'),path=require('path');
const root=path.resolve(__dirname,'../../..'),p=JSON.parse(fs.readFileSync(__dirname+'/protocol.json'));
function gate(){if(Date.now()>=Date.parse(p.deadline))throw Error('Original deadline');}
function sha(file){gate();return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');}
const old=JSON.parse(fs.readFileSync(root+'/research/experiments/miniplayer-foreground-14/verification.json'));let records=[];
for(const r of old.records){gate();const d=root+`/.evidence-working/${r.member==='expanded'?'expanded-geometry-02':'compact-geometry-01'}/${r.reference}`;const c=JSON.parse(fs.readFileSync(d+'/case.json'));if(sha(d+'/case.json')!==r.case_sha256)throw Error('Case mismatch');let layers=[];
for(let i=0;i<r.layers.length;i++){const a=r.layers[i],l=c.foreground_layers[i],asset=l.vector_asset||l.artwork_asset;if(asset!==a.asset||sha(d+'/'+asset)!==a.sha256)throw Error('Asset mismatch');layers.push({asset,sha256:a.sha256,box:l.box,mode:l.mode,exact:true});}
records.push({member:r.member,reference:r.reference,case_sha256:r.case_sha256,layers});}
fs.writeFileSync(__dirname+'/result.json',JSON.stringify({status:'UNCHANGED_IMPLEMENTATION_VERIFIED_FIDELITY_UNRESOLVED',finished:new Date().toISOString(),records,ledger:{case_records:4,asset_layers:20,rays:0,images:0,composites:0,rasterizations:0,fits:0},intervention_selected:false,limits:'Glyph-box residuals include changed backing. Exact UI weight/pose and material remain unproven; no retint or vector change follows.'},null,2)+'\n');
