"""Symmetric archive trace and original SF plus: no screenshot coverage."""
exec(open('/evidence/extended/toolbar-glyph-fit.py').read().split('for name,stem,box in ')[0])
out=out/'clean';out.mkdir(exist_ok=True)
for name,box in [('archivebox',[695,462,872,628]),('plus',[1068,470,1215,618])]:
 a,b,c,d=box;B=C[b-cy:d-cy,a-cx:c-cx];T=target[b:d,a:c]
 def make(v):
  X,Y,H,shape=v
  if name=='archivebox':
   # Three symmetric components; dimensions normalized to the glyph viewbox.
   raw=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 92"><path fill="none" stroke="#000" stroke-width="{shape}" stroke-linejoin="round" d="M12 23V76Q12 86 22 86H78Q88 86 88 76V23"/><rect x="5" y="5" width="90" height="19" rx="6.5" fill="none" stroke="#000" stroke-width="{shape}"/><rect x="32" y="38" width="36" height="{shape}" rx="{shape/2}" fill="#000"/></svg>'.encode();ratio=100/92
  else:
   gs=font.getGlyphSet(location={'wght':shape});pen=SVGPathPen(gs);bounds=BoundsPen(gs);gs['plus.tag.color.large'].draw(pen);gs['plus.tag.color.large'].draw(bounds);x0,y0,x1,y1=bounds.bounds;ratio=(x1-x0)/(y1-y0)
   raw=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {x1-x0} {y1-y0}"><path fill="#000" transform="translate({-x0} {y1}) scale(1 -1)" d="{pen.getCommands()}"/></svg>'.encode()
  W=H*ratio;placement=[X-W/2,Y-H/2,X+W/2,Y+H/2];return raw,placement
 def value(v,detail=False):
  raw,placement=make(v);alpha=_coverage(raw,tuple(box),tuple(placement),1);den=max(float((alpha*alpha).sum()),1e-9);color=np.clip(np.sum(alpha[...,None]*(T-B*(1-alpha[...,None])),axis=(0,1))/den,0,1);pred=B*(1-alpha[...,None])+color*alpha[...,None];err=float(np.mean((pred-T)**2)*255**2)
  return (err,color,pred,raw,placement) if detail else err
 start=[(a+c)/2,(b+d)/2,(d-b)*.93,8 if name=='archivebox' else 300]
 bounds=[(start[0]-8,start[0]+8),(start[1]-8,start[1]+8),((d-b)*.85,(d-b)*1.05),(6,11) if name=='archivebox' else (150,450)]
 fit=minimize(value,start,method='Powell',bounds=bounds,options=dict(maxfev=500,xtol=.001,ftol=1e-8));err,color,pred,raw,placement=value(fit.x,True)
 record=dict(name=name,mse=err,color=color.tolist(),placement=placement,box=box,parameters=fit.x.tolist(),provenance='Symmetric rounded geometric trace; source font lacks matching outline variant' if name=='archivebox' else 'Original SF plus.tag.color.large variable-weight outline',limits='Uniform size and placement, one stroke/weight parameter and constant color; no pixel mask or colored source glyph copied.')
 (out/f'{name}.svg').write_bytes(raw);(out/f'{name}.json').write_text(json.dumps(record,indent=2)+'\n');Image.fromarray(np.uint8(np.rint(np.clip(pred,0,1)*255))).save(out/f'{name}-render.png');print(json.dumps(record),flush=True)
