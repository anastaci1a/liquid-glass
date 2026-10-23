"""Compact paired21 native/source baseline; no fit or source correction."""
import json,os,sys,math
from pathlib import Path
import cv2,numpy as np
ROOT=Path('/evidence/extended/helper-toolbar-work/compact-mini-round')
sys.path.insert(0,str(ROOT/'code'))
from extended_fit import Study
from extended_shadow import shadow
from source_support import masks,kernel_safe,confidence_at,coverage_report,supported
cv2.setNumThreads(1)

def save(name,v):
    (ROOT/name).write_text(json.dumps(v,indent=2)+'\n')

def guards(s,p,pred):
    score=s.scores(pred,include_ssim=False);score['E']=math.sqrt(score['loss'])
    x0,y0,x1,y1=s.crop;complete=s.apply_foreground(pred.copy())
    score['foreground_mse']={}
    for layer in s.case['foreground_layers']:
        a,b,c,d=layer['box'];key=layer.get('style_key',layer.get('vector_asset',layer.get('artwork_asset')))
        score['foreground_mse'][key]=float(np.mean((complete[b-y0:d-y0,a-x0:c-x0]-s.target[b:d,a:c])**2))*255**2
    reference={**p,**s.case['exterior_reference_shape']}
    sd=s.shape(s.x,s.y,reference)[-1][0];defined=cv2.imread(str(s.folder/'known.png'),0)[y0:y1,x0:x1]>0
    ext=(sd>1.5/s.L)&(sd<.2)&defined
    X=s.x*s.L+s.case['center'][0];Y=s.y*s.L+s.case['center'][1]
    for a,b,c,d in s.case.get('exterior_exclusions',[]):ext&=~((X>=a)&(X<=c)&(Y>=b)&(Y<=d))
    clean=s.source[y0:y1,x0:x1]*(1-shadow(s,p,s.x,s.y)[...,None])
    score['exterior']=dict(pixels=int(ext.sum()),rmse=float(np.sqrt(np.mean((clean[ext]-s.target_crop[ext])**2))*255))
    return score,complete,ext

def emitted(s,p,index):
    defined,observed=masks(s);dsafe,radius=kernel_safe(defined,s,p);osafe,_=kernel_safe(observed,s,p)
    counts={k:0 for k in ['whole','scored','whole_defined_bad','whole_observed_bad','scored_defined_bad','scored_observed_bad']}
    minimum={'whole_defined':1.,'whole_observed':1.,'scored_defined':1.,'scored_observed':1.}
    points=[]
    for row,bottom,W,x,y in s.raster_tiles(1):
        sd=s.shape(x,y,p)[-1][0];whole=sd<=0
        score=whole&np.repeat(np.repeat(s.valid[row:bottom],2,axis=0),2,axis=1)
        X,Y,_,_=s.geometry_field(x,y,p);X=X*s.L+s.case['center'][0];Y=Y*s.L+s.case['center'][1]
        dc=confidence_at(dsafe,X,Y);oc=confidence_at(osafe,X,Y)
        for key,mask in [('whole',whole),('scored',score)]:
            counts[key]+=int(mask.sum())
            for kind,c in [('defined',dc),('observed',oc)]:
                counts[key+'_'+kind+'_bad']+=int((mask&(c<.999)).sum())
                if mask.any():minimum[key+'_'+kind]=min(minimum[key+'_'+kind],float(c[mask].min()))
        bad=whole&((dc<.999)|(oc<.999))
        if bad.any():
            points.append(np.stack([x[bad]*s.L+s.case['center'][0],y[bad]*s.L+s.case['center'][1],X[bad],Y[bad],dc[bad],oc[bad],score[bad]],axis=1))
    data=np.concatenate(points) if points else np.empty((0,7))
    np.save(ROOT/f'ref{index}-unsupported-rays.npy',data)
    return dict(scale=1,counts=counts,minimum_confidence=minimum,gaussian_radius_native_px=radius,
                whole_defined_fraction=1-counts['whole_defined_bad']/counts['whole'],whole_observed_fraction=1-counts['whole_observed_bad']/counts['whole'],
                passed=counts['whole_defined_bad']==0 and counts['whole_observed_bad']==0,
                unsupported_rows_columns=['output_x','output_y','source_x','source_y','defined_confidence','observed_confidence','scored_native_pixel'],
                representative_unsupported=data[:12].tolist(),limits='Discrete ORIGINAL native2x2 in-shape emitted rays with original3sigmaGaussian support; no changed masks, source repair, center-only inference or continuous-surface proof.')

def main():
    os.umask(0o002)
    if (ROOT/'preflight-result.json').exists():print('Complete preflight retained; no repeat');return
    if (ROOT/'preflight-started.json').exists():raise RuntimeError('Inspect partial baseline/proof before recovery')
    save('preflight-started.json',dict(pid=os.getpid(),fits=0,baseline='public paired21',source_gate='whole+scored emitted before fitting'))
    state=json.loads((ROOT/'authoritative-paired21.json').read_text());rows=[]
    for i,name in enumerate(['a','b']):
        s=Study(ROOT/name);p=state['parameters'].copy();L=s.case.get('parameter_length_reference',s.L);p['sigma']*=L;p['post_sigma']*=L
        pred=s.render(p,np.asarray(state['material']));scores,complete,ext=guards(s,p,pred)
        assert abs(scores['loss']-state['scores'][i]['loss'])<1e-6,'Authoritative paired21 native mismatch'
        np.save(ROOT/f'ref{i}-baseline-material.npy',pred);np.save(ROOT/f'ref{i}-baseline-complete.npy',complete)
        np.savez_compressed(ROOT/f'ref{i}-frozen-masks.npz',glass=s.valid,rim=s.rim,held=s.held,exterior=ext)
        center=coverage_report(s,p);sub=emitted(s,p,i)
        rows.append(dict(reference=name,scores=scores,native_loss_matches=True,center_support=center,emitted_support=sub))
        save('preflight-partial.json',rows)
        print(name,'E',scores['E'],'whole_bad',sub['counts']['whole_defined_bad'],'scored_bad',sub['counts']['scored_defined_bad'],flush=True)
    save('baseline-native-recipe.json',dict(parameters=p,material=state['material'],scores=[r['scores'] for r in rows]))
    save('preflight-result.json',dict(observations=rows,fit_authorized_by_source=all(supported(Study(ROOT/r['reference']),r['center_support']) and r['emitted_support']['passed'] for r in rows),fits=0,accepted_count=0,source_epoch_unchanged=True,limits='Primary whole-emitted source gate takes precedence. If failed, FLAG BEFORE FIT; do not repair source or infer optical improvement from this native baseline.'))
    print('DONE source_gate',all(r['emitted_support']['passed'] for r in rows),flush=True)

if __name__=='__main__':main()
