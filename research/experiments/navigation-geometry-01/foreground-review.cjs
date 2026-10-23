const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../..');
const accepted=JSON.parse(fs.readFileSync(path.join(root,'reconstruction/studies/music-navigation/review-round/pass-03.json')));
const rows=[];
for(const k of ['a','b']){
 const folder=path.join(root,'.evidence-working/navigation-geometry-01',k),c=JSON.parse(fs.readFileSync(path.join(folder,'case.json')));
 for(const layer of c.foreground_layers){
  const svg=fs.readFileSync(path.join(folder,layer.vector_asset));
  const sha=crypto.createHash('sha256').update(svg).digest('hex');
  if(sha!==layer.vector_sha256||sha!==accepted.vector_sha256[k][layer.vector_asset])throw Error('Vector changed');
  if(/<(?:image|filter|foreignObject)\b|(?:xlink:)?href\s*=/i.test(svg.toString()))throw Error('Unexpected external/raster effect');
  const style=c.foreground_styles?.[layer.style_key||layer.vector_asset]||{};
  rows.push({reference:k,asset:layer.vector_asset,sha256:sha,protected:layer.fit_style!==false,backing_dependent:Boolean(style.response),provenance:layer.vector_provenance?.method||'Recorded font outlines; exact UI weight remains unproven.'});
 }
}
fs.writeFileSync(path.join(__dirname,'foreground-review.json'),JSON.stringify({status:'RETAIN_ORIGINAL_INPUTS_AND_STYLES',rows,new_candidates:0,new_fonts:0,new_rays:0,conclusion:'Original hashes match. Home response depends on its backing; other fixed styles are not authority to replace that nonlinear chain. Body/tone errors remain confounders, so no foreground fit is justified here.'},null,2)+'\n');
console.log('Verified 18 retained vector layers; no new foreground candidate.');
