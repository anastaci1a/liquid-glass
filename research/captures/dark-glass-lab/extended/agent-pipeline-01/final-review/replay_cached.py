"""LEAD review only: fixed cached-material/composite replay, no ray/source lookup.
Not a full independent public geometric replay; never restarts expired studies.
"""
from pathlib import Path
import argparse,sys,json,numpy as np
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'code'))
from extended_fit import Study
from geometric_render import coverage_blur
from case_metrics import scores
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False);state=json.loads((P/'working-state.json').read_text());out={}
for key in ['a','b']:
 s=Study(P/f'inputs/{key}');L=np.load(P/'blurriness'/f'{key}-lens-color.npy');alpha=np.load(P/'blurriness'/f'{key}-coverage.npy');clear=np.load(P/'blurriness'/f'{key}-clear-premultiplied.npy');B=coverage_blur(state['color']['g']*L+state['color']['b'],alpha,state['ordinary_output_sigma_native_px']);M=(alpha[...,None]*B+clear).astype(np.float32);C=s.apply_foreground(M.copy());old=np.load(P/state['arrays'][key]['complete']);finite=np.isfinite(old);assert np.array_equal(np.isnan(C),np.isnan(old));assert np.array_equal(C[finite],old[finite]);np.save(a.output/f'{key}-complete.npy',C);out[key]={'cached_composite_pixel_exact':True,'scores':scores(s,np.load(P/f'historical-{key}-masks.npz'),C)}
(a.output/'review.json').write_text(json.dumps({'new_rays':0,'new_source_queries':0,'not_full_geometry_replay':True,'acceptance':False,'cases':out},indent=2))
