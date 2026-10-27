(()=>{
 const color=document.querySelector('[data-outline-range]');if(!color)return;
 const thickness=document.getElementById('outline-thickness'),status=document.getElementById('outline-range-status');let request=0;
 const ready=fetch(color.dataset.outlineRange).then(r=>{if(!r.ok)throw Error('Cannot load outline choices');return r.json();});
 const change=async()=>{
  const id=++request,c=Number(color.value),w=Number(thickness.value),label=`Color ${String.fromCharCode(65+c)} · ${100+20*w}%`;status.textContent='Loading '+label+'…';
  try{
   const sources=await ready;const changes=[...document.querySelectorAll('img[data-comparison-top]')].map(image=>{
    const initial=image.dataset.outlineInitial||(image.dataset.outlineInitial=(image.getAttribute('src')||image.dataset.mediaSrc).split('?')[0]);const matrix=sources[initial];if(!matrix)throw Error('Missing outline choice: '+initial);return {image,choice:matrix[c][w]};
   });
   await Promise.all(changes.filter(x=>!x.image.closest('details')||x.image.closest('details').open).map(({choice})=>new Promise((resolve,reject)=>{const im=new Image();im.onload=resolve;im.onerror=reject;im.src=choice.src;})));
   if(id!==request)return;
   for(const {image,choice} of changes){if(image.hasAttribute('src'))image.src=choice.src;else image.dataset.mediaSrc=choice.src;image.dataset.comparisonRightLabel=choice.label;image.dispatchEvent(new CustomEvent('comparison-source-change',{detail:{rightLabel:choice.label}}));}status.textContent=label;
  }catch(e){status.textContent='Could not load this choice. Please retry.';console.error(e);}
 };color.addEventListener('change',change);thickness.addEventListener('change',change);
})();
