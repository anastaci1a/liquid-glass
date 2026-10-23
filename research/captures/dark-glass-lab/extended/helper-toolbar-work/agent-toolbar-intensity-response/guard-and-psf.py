"""Additional saved-array guard/PSF comparisons; no feature traversal/render."""
import json
from pathlib import Path
import sys
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import toolbar_candidate as model
from PIL import Image
root=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-intensity-response');package=Path('/tmp/agent-toolbar-evidence-package');p=json.loads((package/'recipe.json').read_text());case=p['case'];x0,y0,x1,y1=case['crop'];C=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');a=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');g=np.load(root/'gamma-derivative.npy');source=np.asarray(Image.open(package/'inputs/source.png'),float)[y0:y1,x0:x1]/255;T=np.asarray(Image.open(package/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255;masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');cohorts=np.load('/tmp/agent-toolbar-revision2-identifiability/support-cohorts.npz');fg=np.load(package/'derived-foreground.npz');shadow=model.gaussian_coverage_shadow(case,p);full=C*a[...,None]+source*(1-shadow[...,None])*(1-a[...,None]);dfull=g*a[...,None]
slopes={}
for n in ['glass','rim']:slopes[n]=float(np.mean(2*(C-T)[masks[n]]*g[masks[n]])*255**2)
slopes['exterior']=float(np.mean(2*(full-T)[masks['exterior']]*dfull[masks['exterior']])*255**2)
for layer in p['foreground_layers']:
    aa=fg[layer['name']][...,None];full=full*(1-aa)+np.asarray(layer['color'])*aa;dfull=dfull*(1-aa)
for layer in p['foreground_layers']:
    b,c,d,e=layer['box'];sl=(slice(c-y0,e-y0),slice(b-x0,d-x0));slopes[layer['name']]=float(np.mean(2*(full-T)[sl]*dfull[sl])*255**2)
delta=np.load('/tmp/agent-toolbar-revision2-blur/best-raw/material.npy')-C;comparison={}
for name in ['all','observed_kernel_proxy','estimated_kernel_proxy','mixed_or_uncertain']:
    m=cohorts[name];u=g[m].ravel().astype(float);v=delta[m].ravel().astype(float);comparison[name]={'gamma_vs_saved_blur6_aggregate_secant_cosine':float(u@v/max(np.linalg.norm(u)*np.linalg.norm(v),1e-30)),'saved_secant_change_RMS_255':float(np.sqrt(np.mean(v*v))*255)}
out={'gamma_MSE_derivative_per_unit':slopes,'saved_blur6_secant':comparison,'limits':'Blur6 secant combines source/output width changes, not independent source-PSF Jacobians or a new trial. Guard slopes are local and do not prove nonlinear feasibility. Current native candidate derivatives only; no source/epoch adoption.'};(root/'guard-and-psf.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
