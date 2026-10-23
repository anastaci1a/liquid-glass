"""ONE short existing compact rim-width neighborhood after full source gate."""
import importlib.util,json,os
from pathlib import Path
import cv2,numpy as np
ROOT=Path('/evidence/extended/expanded-mini-short-round');OUT=ROOT/'rim-width-neighborhood'
spec=importlib.util.spec_from_file_location('compact_preflight',ROOT/'preflight.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
from motion_support import complete as complete_source
from preview_size import dimensions

def save(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n')

def good(scores,baseline):
    return all(s['E']<=b['E'] and s['glass']['rmse']<=b['glass']['rmse'] and s['exterior']['rmse']<=b['exterior']['rmse'] and all(s['foreground_mse'][k]<=v for k,v in b['foreground_mse'].items()) for s,b in zip(scores,baseline))

def composition(s,p,pred,presentation=False):
    x0,y0,x1,y1=s.crop
    source=s.source
    if presentation:
        known=cv2.imread(str(s.folder/'known.png'),0).astype(np.float32)/255
        source=complete_source(s,known)
    background=source[y0:y1,x0:x1]*(1-m.shadow(s,p,s.x,s.y)[...,None])
    alpha=s.shape_coverage(p)
    return s.apply_foreground((pred*alpha[...,None]+background*(1-alpha[...,None])).astype(np.float32))

