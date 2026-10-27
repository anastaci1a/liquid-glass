(()=>{
 const select=document.querySelector('[data-outline-options]');if(!select)return;
 const status=document.getElementById('outline-step-status');let request=0;
 const ready=fetch(select.dataset.outlineOptions).then(r=>{if(!r.ok)throw Error('Cannot load outline choices');return r.json();});
 select.addEventListener('change',async()=>{
  const id=++request,index=Number(select.value);status.textContent='Loading '+select.options[index].text+'…';
  try{
   const sources=await ready;
   const changes=[...document.querySelectorAll('img[data-comparison-top]')].map(image=>{
    const initial=image.dataset.outlineInitial||(image.dataset.outlineInitial=(image.getAttribute('src')||image.dataset.mediaSrc).split('?')[0]);const choice=sources[initial];if(!choice)throw Error('Missing outline choice: '+initial);
    return {image,choice:choice[index]};
   });
   await Promise.all(changes.filter(x=>!x.image.closest('details')||x.image.closest('details').open).map(({choice})=>new Promise((resolve,reject)=>{const im=new Image();im.onload=resolve;im.onerror=reject;im.src=choice.src;})));
   if(id!==request)return;
   for(const {image,choice} of changes){if(image.hasAttribute('src'))image.src=choice.src;else image.dataset.mediaSrc=choice.src;image.dataset.comparisonRightLabel=choice.label;image.dispatchEvent(new CustomEvent('comparison-source-change',{detail:{rightLabel:choice.label}}));}
   status.textContent=select.options[index].text;
  }catch(e){status.textContent='Could not load this option. Please retry.';console.error(e);}
 });
})();
