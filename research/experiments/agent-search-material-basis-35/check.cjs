const fs=require('fs'),crypto=require('crypto');
const O=__dirname,P=JSON.parse(fs.readFileSync(O+'/protocol.json'));
function gate(cp=false){if(Date.now()>=Date.parse(P[cp?'checkpoint_deadline':'deadline']))throw Error('Original deadline');}
function save(f,x){gate();fs.writeFileSync(O+'/'+f,JSON.stringify(x,null,2)+'\n');}
const T=P.transmission,k=T**(1/2.4),whiteCeiling=1.055*T**(1/2.4)-.055;
function decode(c){return c<=.04045?c/12.92:((c+.055)/1.055)**2.4;}
function encode(c){if(c<0)throw Error('Negative linear sample');return c<=.0031308?12.92*c:1.055*c**(1/2.4)-.055;}
const clamp=x=>Math.max(0,Math.min(1,x));let records=[],samples=0;
for(const a of P.sets){
 gate();const gn=a.gain/k,bn=(a.bias+.055)/k-.055,lo=Math.min(a.bias,a.gain+a.bias),hi=Math.max(a.bias,a.gain+a.bias),newlo=Math.min(bn,gn+bn),newhi=Math.max(bn,gn+bn);
 const high=lo>.04045,unclipped=lo>=0&&hi<=1&&newlo>=0&&newhi<=1;
 const rec={...a,k,new_gain:gn,new_bias:bn,old_range:[lo,hi],new_range:[newlo,newhi],old_wholly_high_branch:high,new_wholly_high_branch:newlo>.04045,unclipped_full_unit_input:unclipped,full_range_applicable:high&&unclipped,white_ceiling: whiteCeiling,maximum_unclipped_input:a.gain>0?(whiteCeiling-a.bias)/a.gain:null,samples:[]};
 for(const s of P.fixed_samples){
  gate();if(++samples>P.caps.synthetic_scalar_samples)throw Error('Sample cap');const old=a.gain*s+a.bias,converted=gn*s+bn;const unbounded=encode(T*decode(converted)),bounded=encode(T*decode(clamp(converted)));
  rec.samples.push({input:s,old_response:old,new_response_unclipped:converted,new_clips:converted<0||converted>1,output_without_clip:unbounded,output_with_standard_clip:bounded,error_without_clip:unbounded-old,error_with_clip:bounded-old});
 }
 rec.max_abs_unclipped_error=Math.max(...rec.samples.map(x=>Math.abs(x.error_without_clip)));rec.max_abs_standard_clipping_error=Math.max(...rec.samples.map(x=>Math.abs(x.error_with_clip)));records.push(rec);
}
gate(true);save('checkpoint.json',{at:new Date().toISOString(),four_sets_complete:true,samples,scalar_algebra_only:true,high_branch_sets:records.filter(x=>x.old_wholly_high_branch).map(x=>x.name),fully_applicable:records.filter(x=>x.full_range_applicable).map(x=>x.name)});
save('result.json',{status:'ANALYTIC_PREREQUISITE_COMPLETE_WITH_BRANCH_AND_CLIPPING_LIMITS',finished:new Date().toISOString(),T,k,whiteCeiling,records,ledger:{coefficient_sets:records.length,synthetic_scalar_samples:samples,optical_or_image_work:0,shared_numerical_imports:0},selected_state_changed:false});
console.log(records.map(x=>({name:x.name,full:x.full_range_applicable,range:x.new_range,max_error:x.max_abs_standard_clipping_error,limit:x.maximum_unclipped_input})));
