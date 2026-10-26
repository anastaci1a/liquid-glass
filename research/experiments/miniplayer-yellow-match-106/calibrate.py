"""One exact yellow endpoint with bounded HSV curves and a local hue adjustment."""
from pathlib import Path
import json,datetime,hashlib,colorsys,traceback,copy
import numpy as np
from scipy.interpolate import PchipInterpolator,CubicHermiteSpline
from miniplayer_anchor_color import adjusted_outline_endpoint,outline_endpoint,curve
from environment_radiance import decode_srgb
B=Path(__file__).resolve().parent;P=json.loads((B/'protocol.json').read_text());OLD=B.parent/'miniplayer-final-white-105';END=datetime.datetime.fromisoformat(P['checkpoint_deadline']);ledger=dict(calibration_scalar_points=0,control_colors=0)
def save(n,v):(B/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
    assert datetime.datetime.now(datetime.timezone.utc)<END;assert ledger[k]+n<=P['caps'][k];ledger[k]+=int(n)
def rgb(h):return np.array([int(h[i:i+2],16)/255 for i in (0,2,4)])
def specification(x,y):
    m=PchipInterpolator(x,y).derivative()(x);m[[0,-1]]=0
    return dict(x=x.tolist(),y=y.tolist(),slopes=m.tolist())
save('calibration-start.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),deadline=P['checkpoint_deadline']))
try:
    C=copy.deepcopy(json.loads((OLD/'calibration.json').read_text()));inputs=['FFFFFF',P['input_anchor'],'B28E3E','C59352'];targets=['FCFCFC',P['target_anchor'],'F6DDAD','FBD7A1'];raw=np.array([rgb(x) for x in inputs]);target=np.array([rgb(x) for x in targets]);ih=np.array([colorsys.rgb_to_hsv(*x) for x in raw]);th=np.array([colorsys.rgb_to_hsv(*x) for x in target]);order=np.argsort(ih[1:,2]);x=ih[1:,2][order];s=ih[1:,1][order];t=th[1:][order];role=C['roles']['outline'];N=curve(x,role['neutral'])
    role['saturation_multiplier']=specification(x,t[:,1]/s);role['value_logit_offset']=specification(x,(np.log(t[:,2]/(1-t[:,2]))-np.log(N/(1-N)))/s)
    shift=(th[1,0]-ih[1,0]+.5)%1-.5;offset=np.array([shift,0,0])[order];C['outline_hue_adjustment']=dict(center_hue=float(ih[1,0]),half_width=P['outline_half_width_hue_degrees']/360,offset_curve=specification(x,offset));C['anchors']['outline']=[dict(input=i,target=o) for i,o in zip(inputs,targets)];C['hue']='Local warm-hue correction explicitly required by the new exact yellow anchor; old API/default behavior unchanged';C['kind']='Outline-only color calibration; body response unchanged from105'
    actual=adjusted_outline_endpoint(raw,C);charge('control_colors',4);assert np.max(abs(actual[1]-target[1]))<1e-14
    ah=np.array([colorsys.rgb_to_hsv(*a) for a in actual]);assert np.max(abs(ah[:,1:]-th[:,1:]))<1e-12;assert np.max(abs(actual[0]-target[0]))<1e-14
    checks=[dict(input=i,target=t,output_hex=''.join(f'{round(v*255):02X}' for v in a),output=a.tolist(),RGB_error_255=((a-b)*255).tolist()) for i,t,a,b in zip(inputs,targets,actual,target)]
    observed=np.array([rgb(P[k]) for k in ['input_anchor','observed_current','target_anchor']]);charge('control_colors',3);obs=[]
    for k,a in zip(['input','reported_current','requested'],observed):
        h,s,v=colorsys.rgb_to_hsv(*a);obs.append(dict(role=k,RGB_255=(a*255).tolist(),hue_degrees=h*360,saturation=s,value=v,encoded_luma=float(a@np.array([.2126,.7152,.0722])),linear_luminance=float(decode_srgb(a)@np.array([.2126,.7152,.0722]))))
    save('color-comparison.json',dict(colors=obs,RGB_change_current_to_target=((observed[2]-observed[1])*255).tolist(),saturation_ratio=obs[2]['saturation']/obs[1]['saturation'],required_input_hue_shift_degrees=shift*360,input_correspondence='User-supplied tentative preimage, not independently identified',exact_yellow_anchor=True))
    for sp in [role['saturation_multiplier'],role['value_logit_offset'],C['outline_hue_adjustment']['offset_curve']]:
        xx=np.linspace(0,1,10001);yy=curve(xx,sp);charge('calibration_scalar_points',len(xx));assert yy.min()>=min(sp['y'])-1e-12 and yy.max()<=max(sp['y'])+1e-12
    sweep=np.array([colorsys.hsv_to_rgb(h,s,v) for h in np.linspace(0,1,24,endpoint=False) for s in np.linspace(0,1,33) for v in np.linspace(0,1,65)]);out=adjusted_outline_endpoint(sweep,C);charge('control_colors',len(sweep));assert np.isfinite(out).all() and out.min()>=0 and out.max()<=1
    gray=np.repeat(np.linspace(0,1,4097)[:,None],3,axis=1);a=adjusted_outline_endpoint(gray,C);old=outline_endpoint(gray,json.loads((OLD/'calibration.json').read_text()));charge('control_colors',len(gray));assert np.array_equal(a,old) and np.all(np.diff(a[:,0])>=-1e-12)
    # Separate scalar colorsys reconstruction with SciPy interpolation.
    splines={k:CubicHermiteSpline(role[k]['x'],role[k]['y'],role[k]['slopes']) for k in ['neutral','saturation_multiplier','value_logit_offset']};hs=C['outline_hue_adjustment']['offset_curve'];hf=CubicHermiteSpline(hs['x'],hs['y'],hs['slopes']);ids=np.linspace(0,len(sweep)-1,4096,dtype=int);other=[]
    for a in sweep[ids]:
        h,s,v=colorsys.rgb_to_hsv(*a);z={k:float(f(np.clip(v,role[k]['x'][0],role[k]['x'][-1]))) for k,f in splines.items()};N=z['neutral'];V=1/(1+np.exp(-(np.log(N/(1-N))+s*z['value_logit_offset'])));delta=(h-C['outline_hue_adjustment']['center_hue']+.5)%1-.5;width=C['outline_hue_adjustment']['half_width'];w=.5*(1+np.cos(np.pi*delta/width)) if abs(delta)<width else 0.;h+=(float(hf(np.clip(v,hs['x'][0],hs['x'][-1])))*w if s>0 else 0);other.append(colorsys.hsv_to_rgb(h%1,s*z['saturation_multiplier'],V))
    charge('control_colors',len(ids));error=float(np.max(abs(np.array(other)-out[ids])));assert error<2e-14
    save('calibration.json',C);save('calibration-checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),anchors=checks,passed=True,neutral_exact=True,independent_error=error,grid_colors=len(sweep),minimum=float(out.min()),maximum=float(out.max()),ledger=ledger));print('COLOR PASS',json.loads((B/'color-comparison.json').read_text()),flush=True)
except Exception as e:save('calibration-failure.json',dict(error=repr(e),traceback=traceback.format_exc(),ledger=ledger));raise
finally:save('calibration-ledger.json',ledger)
