"""Fit one reusable symmetric outline icon, not a screenshot stencil."""
exec(open('/evidence/extended/toolbar-glyph-fit.py').read().split('for name,stem,box in ')[0])
out=out/'arcs';out.mkdir(exist_ok=True);box=[695,462,872,628];a,b,c,d=box;B=C[b-cy:d-cy,a-cx:c-cx];T=target[b:d,a:c]
def geometry(v):
 X,Y,W,H,s,lid,inset,r,hw,hy=v;s*=100;h=100*H/W;lid*=h;hy*=h;inset*=100;r*=100;hw*=100
 raw=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 {h}"><path fill="none" stroke="#000" stroke-width="{s}" stroke-linejoin="round" d="M{inset+s/2} {lid-s/2}V{h-s/2-r}A{r} {r} 0 0 0 {inset+s/2+r} {h-s/2}H{100-inset-s/2-r}A{r} {r} 0 0 0 {100-inset-s/2} {h-s/2-r}V{lid-s/2}"/><rect x="{s/2}" y="{s/2}" width="{100-s}" height="{lid-s}" rx="{r}" fill="none" stroke="#000" stroke-width="{s}"/><rect x="{50-hw/2}" y="{hy-s/2}" width="{hw}" height="{s}" rx="{s/2}" fill="#000"/></svg>'.encode();return raw,[X-W/2,Y-H/2,X+W/2,Y+H/2]
def objective(v,details=False):
 raw,pose=geometry(v);alpha=_coverage(raw,tuple(box),tuple(pose),1);color=np.clip(np.sum(alpha[...,None]*(T-B*(1-alpha[...,None])),axis=(0,1))/max(float((alpha**2).sum()),1e-9),0,1);pred=B*(1-alpha[...,None])+color*alpha[...,None];mse=float(np.mean((pred-T)**2)*255**2)
 return (mse,raw,pose,color,pred) if details else mse
v=[782.5,545,156,144,.09,.30,.07,.055,.4,.47]
bounds=[(777,787),(540,550),(150,164),(135,151),(.075,.105),(.25,.35),(.05,.10),(.035,.09),(.33,.45),(.42,.52)]
fit=minimize(objective,v,method='Powell',bounds=bounds,options=dict(maxfev=1800,xtol=1e-5,ftol=1e-9));mse,raw,pose,color,pred=objective(fit.x,True)
record=dict(name='archivebox',mse=mse,color=color.tolist(),placement=pose,box=box,parameters=fit.x.tolist(),provenance='Symmetric rounded outline trace; original font exposes a mismatched filled base glyph.',limits='Three clean vector components; uniform stroke, shared corner radius, horizontal symmetry. Geometry is an independently reconstructed icon, not exact original Apple outline. No screenshot alpha or per-pixel correction.')
(out/'archivebox.svg').write_bytes(raw);(out/'archivebox.json').write_text(json.dumps(record,indent=2)+'\n');Image.fromarray(np.uint8(np.rint(np.clip(pred,0,1)*255))).save(out/'archivebox-render.png');print(json.dumps(record),flush=True)
