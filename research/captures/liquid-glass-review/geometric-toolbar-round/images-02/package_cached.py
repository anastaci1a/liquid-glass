"""Presentation/measurements of SAVED images and geometry only; no tracing."""
from pathlib import Path
import json,sys
P=Path(__file__).resolve().parent
import numpy as np,cv2
from PIL import Image
sys.path.insert(0,str(P))
f=json.loads((P/'frozen-inputs.json').read_text());p=f['old_filtered_recipe'];x0,y0,x1,y1=p['case']['crop'];H,W=y1-y0,x1-x0
reg=json.loads(Path('/tmp/agent-toolbar-run/input-audit.json').read_text())['registration'];A=np.array(reg['matrix'])
estimated=np.zeros((1080,1920),np.uint8);estimated[350:790,490:1420]=1;estimated=cv2.warpAffine(estimated,A,(1920,1080),flags=cv2.INTER_NEAREST)>0
masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');T=np.asarray(Image.open('/tmp/agent-toolbar-evidence-package/inputs/target.png'),float)[y0:y1,x0:x1]/255
historical=np.load('/evidence/extended/toolbar-response-primary-review/complete.npy');historicalM=np.load('/evidence/extended/toolbar-response-primary-review/material.npy')
def metric(a,m):
    d=(a-T)[m]*255
    return {'pixels':int(m.sum()),'rmse':float(np.sqrt(np.mean(d*d)))}
out={'source_proof':'No new samples or ray queries. All fields derive from cached preflight and native arrays.','historical_descriptive':{k:metric(historicalM if k!='exterior' else historical,masks[k]) for k in masks.files},'depths':{}}
for tag in ['0.02','0.04']:
    X=np.load(P/f'X-{tag}.npy',mmap_mode='r');Y=np.load(P/f'Y-{tag}.npy',mmap_mode='r');inside=np.load(P/f'inside-{tag}.npy',mmap_mode='r')
    r={'inside_bounds_min':[1e30,1e30],'inside_bounds_max':[-1e30,-1e30],'maximum_displacement_px':0.,'inside_queries':0,'inside_estimated_footprints':0,'horizontal_derivative_min':1e30,'horizontal_derivative_max':-1e30,'foreground':{}}
    for top in range(0,H*4,48):
        bot=min(top+48,H*4);u=X[top:bot];v=Y[top:bot];active=inside[top:bot]
        if not active.any():continue
        yy,xx=np.mgrid[top:bot,:W*4];nativeX=x0+(xx+.5)/4-.5;nativeY=y0+(yy+.5)/4-.5
        r['maximum_displacement_px']=max(r['maximum_displacement_px'],float(np.hypot(u-nativeX,v-nativeY)[active].max()))
        r['inside_bounds_min']=np.minimum(r['inside_bounds_min'],[u[active].min(),v[active].min()]).tolist();r['inside_bounds_max']=np.maximum(r['inside_bounds_max'],[u[active].max(),v[active].max()]).tolist()
        ix=np.floor(u).astype(int);iy=np.floor(v).astype(int)
        e=estimated[iy,ix]|estimated[iy,ix+1]|estimated[iy+1,ix]|estimated[iy+1,ix+1]
        r['inside_queries']+=int(active.sum());r['inside_estimated_footprints']+=int((e&active).sum())
        local=active[:,1:-1]&active[:,:-2]&active[:,2:]
        if local.any():
            dx=(u[:,2:]-u[:,:-2])/.5
            r['horizontal_derivative_min']=min(r['horizontal_derivative_min'],float(dx[local].min()));r['horizontal_derivative_max']=max(r['horizontal_derivative_max'],float(dx[local].max()))
    C=np.load(P/f'complete-{tag}.npy')
    for l in p['foreground_layers']:
        a,b,c,d=l['box'];mask=np.zeros((H,W),bool);mask[b-y0:d-y0,a-x0:c-x0]=1
        r['foreground'][l['name']]=metric(C,mask)
    out['depths'][tag]=r
    geo=np.load(P/f'actual-sections-rays-{tag}.npz')
    # SVG scientific sections from saved geometry: no raster renderer needed.
    elements=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="450" viewBox="0 0 1200 450"><rect width="1200" height="450" fill="white"/>','<text x="20" y="22" font-size="16">Actual same-surface sections; red ray segments shortened. Exact crease unresolved.</text>']
    for panel,(axis,coord,extent) in enumerate([('x',0,392/170),('y',1,1)]):
        def point(u,z):return (panel*600+50+(u/extent+1)*250,75+(.04-z)/.21*300)
        def line(vertices,color):
            pairs=[point(v[coord],v[2]) for v in vertices if np.isfinite(v).all()]
            elements.append('<polyline fill="none" stroke="'+color+'" stroke-width="1.5" points="'+' '.join(f'{u:.5f},{v:.5f}' for u,v in pairs)+'"/>')
        line(geo[f'{axis}_front'],'black');line(geo[f'{axis}_back'],'blue')
        if axis=='x':
            for b,d in zip(geo['ray_back'][::3],geo['ray_exit'][::3]):
                line(np.array([[b[0],b[1],.025],b]),'gray');line(np.array([b,b+.12*d]),'red')
        elements.append(f'<text x="{panel*600+55}" y="420" font-size="16">Depth {tag}; {axis}/L section; front black, back blue; z/L upward</text>')
    elements.append('</svg>');(P/f'sections-rays-{tag}.svg').write_text(''.join(elements))
(P/'cached-geometry-summary.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
