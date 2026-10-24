// Saved event JSON only. No optical functions, numerical cache or source images.
const fs=require('fs');
const p=__dirname+'/';
if(Date.now()>=Date.parse('2026-10-24T04:13:58.207Z'))throw Error('Packaging deadline');
const r=JSON.parse(fs.readFileSync(p+'result.json'));
let down=0,other=0,blocked=0,critical=0,rounded=0,maxClosure=0;
const unsupported={a:{raw:0,incident_compatible:0},b:{raw:0,incident_compatible:0}};
const plane={position:0,direction:0,normal:0};
const powers={a:{raw:{},incident_compatible:{}},b:{raw:{},incident_compatible:{}}};
const rows=[];
for(const l of r.launches){
 rows.push({labels:l.selection.labels.map(x=>x.axis+' '+x.fraction),position:l.selection.position,termination:l.termination,nested:l.nested_actual,levels:l.level_actual});
 for(const k of ['a','b'])for(const role of ['raw','incident_compatible']){
  for(const [cat,sp] of Object.entries(l.partition_serialized[k][role])){
   if(!powers[k][role][cat])powers[k][role][cat]=[];
   powers[k][role][cat].push(sp[0]+sp[1]);
  }
 }
 for(const roles of Object.values(l.closure))for(const errors of Object.values(roles))for(const e of errors)maxClosure=Math.max(maxClosure,Math.abs(e));
 for(const ev of l.events){
  if(ev.transmission_blocked)blocked++;
  if(ev.critical)critical++;
  if(ev.R_one_without_TIR)rounded++;
  for(const key of ['plane','transmitted_plane'])if(ev[key])for(const name of Object.keys(plane))plane[name]=Math.max(plane[name],ev[key][name]??0);
  if(ev.endpoint){
   if(ev.endpoint.role==='downward_background'){
    down++;
    for(const k of ['a','b'])for(const role of ['raw','incident_compatible'])if(!ev.endpoint.availability[k][role])unsupported[k][role]++;
   }else other++;
  }
 }
}
for(const k of ['a','b'])for(const role of ['raw','incident_compatible'])for(const [cat,values] of Object.entries(powers[k][role])){
 powers[k][role][cat]={equal_launch_mean:values.reduce((a,b)=>a+b,0)/values.length,min:Math.min(...values),max:Math.max(...values)};
}
const result={status:r.status,scope:'Saved JSON only; equal-weight16 selected launches, not spatial/image/radiance weights.',launches:r.launches.length,downward_endpoints:down,other_transmitted_endpoints:other,blocked_transmissions:blocked,critical_exact:critical,R_one_without_TIR:rounded,unsupported_endpoints:unsupported,power_summaries:powers,max_component_closure_error:maxClosure,max_plane_residual:plane,launches_summary:rows};
fs.writeFileSync(p+'summary.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
