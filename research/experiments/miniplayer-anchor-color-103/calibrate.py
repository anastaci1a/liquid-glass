"""Derive one bounded pair of HSV maps; no image or optical evaluation."""
from pathlib import Path
import json,datetime,hashlib,colorsys,traceback
import numpy as np
from scipy.interpolate import PchipInterpolator,CubicHermiteSpline
from miniplayer_refinement_effects import low_luminance_body
from miniplayer_color_refinement import bright_colored_rim
from environment_radiance import decode_srgb,encode_srgb
from miniplayer_anchor_color import response,curve
B=Path(__file__).resolve().parent;R=B.parents[2];P=json.loads((B/'protocol.json').read_text());F=json.loads((B/'frozen-family.json').read_text())
deadline=datetime.datetime.fromisoformat(P['start'])+datetime.timedelta(minutes=P['calibration_checkpoint_minutes']);ledger=dict(calibration_scalar_points=0,control_colors=0)
def charge(k,n):
    assert datetime.datetime.now(datetime.timezone.utc)<deadline;assert ledger[k]+n<=P['caps'][k];ledger[k]+=int(n)
def save(n,v):(B/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def rgb(h):return np.array([int(h[i:i+2],16)/255 for i in (0,2,4)])
def spec(x,y,flat=False):
    slopes=PchipInterpolator(x,y).derivative()(x)
    if flat:slopes[[0,-1]]=0
    return dict(x=x.tolist(),y=y.tolist(),slopes=slopes.tolist())
save('calibration-start.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),deadline=deadline.isoformat(),scope='Scalar calibration and color controls only'))
try:
    values=np.linspace(0,1,4097);gray=np.repeat(values[:,None],3,axis=1);mat=F['material'];n=F['optics']['index'];normal_power=(1-((n-1)/(n+1))**2)**2
    # Freeze the old neutral response only as a curve-shape/black-point prior.
    old_body=encode_srgb(normal_power*decode_srgb(low_luminance_body(gray,mat['gain'],mat['bias'],mat['low_luminance_lift'])))
    old_rim=bright_colored_rim(old_body,gray,np.ones(len(gray)),**mat['outline']['endpoint'])
    charge('calibration_scalar_points',2*len(gray));inputs=np.array([rgb(x) for x in P['inputs']]);input_hsv=np.array([colorsys.rgb_to_hsv(*x) for x in inputs]);order=np.argsort(input_hsv[1:,2]);x=input_hsv[1:,2][order]
    C=dict(kind='Held direct final display calibration',color_space='encoded sRGB / HSV',hue='preserved exactly',normal_power_prior=normal_power,baseline_family_sha256=hashlib.sha256((B/'frozen-family.json').read_bytes()).hexdigest(),roles={},anchors={})
    checks=[]
    for role,prior in [('body',old_body),('outline',old_rim)]:
        target=np.array([rgb(x) for x in P[role+'_targets']]);target_hsv=np.array([colorsys.rgb_to_hsv(*x) for x in target]);prior=prior[:,0]
        neutral=prior[0]+(target[0,0]-prior[0])*(prior-prior[0])/(prior[-1]-prior[0]);assert np.all(np.diff(neutral)>=-1e-12) and np.all((neutral>0)&(neutral<1))
        neutral_spec=spec(values,neutral);N=curve(x,neutral_spec);s=input_hsv[1:,1][order];sat=target_hsv[1:,1][order];v=target_hsv[1:,2][order]
        multiplier=sat/s;offset=(np.log(v/(1-v))-np.log(N/(1-N)))/s
        C['roles'][role]=dict(neutral=neutral_spec,saturation_multiplier=spec(x,multiplier,True),value_logit_offset=spec(x,offset,True),black_prior=float(prior[0]),white_target=float(target[0,0]))
        C['anchors'][role]=[dict(input=i,target=o) for i,o in zip(P['inputs'],P[role+'_targets'])]
        actual=response(inputs,C['roles'][role]);charge('control_colors',len(inputs));actual_hsv=np.array([colorsys.rgb_to_hsv(*a) for a in actual]);assert np.max(abs(actual_hsv[:,1:]-target_hsv[:,1:]))<1e-12
        for i in range(4):
            hx=''.join(f'{round(z*255):02X}' for z in actual[i]);hue_error=0 if input_hsv[i,1]==0 else float(abs(actual_hsv[i,0]-input_hsv[i,0]));assert hue_error<1e-12
            checks.append(dict(role=role,input=P['inputs'][i],target=P[role+'_targets'][i],hue_preserved_output=hx,output=actual[i].tolist(),saturation_error=float(actual_hsv[i,1]-target_hsv[i,1]),value_error=float(actual_hsv[i,2]-target_hsv[i,2]),hue_error=hue_error,RGB_error_255=((actual[i]-target[i])*255).tolist()))
        assert ''.join(f'{round(z*255):02X}' for z in actual[0])==P[role+'_targets'][0]
        for name in ['saturation_multiplier','value_logit_offset']:
            sp=C['roles'][role][name];dense=np.linspace(0,1,10001);out=curve(dense,sp);charge('calibration_scalar_points',len(dense));assert out.min()>=min(sp['y'])-1e-12 and out.max()<=max(sp['y'])+1e-12
            assert sp['slopes'][0]==sp['slopes'][-1]==0
    sweep=np.array([colorsys.hsv_to_rgb(h,s,v) for h in np.linspace(0,1,24,endpoint=False) for s in np.linspace(0,1,33) for v in np.linspace(0,1,65)])
    grid=[]
    for role in ['body','outline']:
        out=response(sweep,C['roles'][role]);charge('control_colors',len(sweep));assert np.isfinite(out).all() and out.min()>=0 and out.max()<=1
        gray_out=response(gray,C['roles'][role]);charge('control_colors',len(gray));assert np.max(np.ptp(gray_out,axis=1))==0 and np.all(np.diff(gray_out[:,0])>=-1e-12)
        # Independent SciPy interpolation and scalar HSV reconstruction at fixed grid points.
        ids=np.linspace(0,len(sweep)-1,4096,dtype=int);sc=C['roles'][role];splines={k:CubicHermiteSpline(v['x'],v['y'],v['slopes']) for k,v in sc.items() if isinstance(v,dict)};other=[]
        for color in sweep[ids]:
            h,s,v=colorsys.rgb_to_hsv(*color);z={k:float(f(np.clip(v,sc[k]['x'][0],sc[k]['x'][-1]))) for k,f in splines.items()};N=z['neutral'];V=1/(1+np.exp(-(np.log(N/(1-N))+s*z['value_logit_offset'])));other.append(colorsys.hsv_to_rgb(h,s*z['saturation_multiplier'],V))
        charge('control_colors',len(ids));error=float(np.max(abs(np.array(other)-out[ids])));assert error<2e-14
        grid.append(dict(role=role,grid_colors=len(sweep),minimum=float(out.min()),maximum=float(out.max()),independent_maximum_error=error,neutral_monotone=True))
    save('calibration.json',C);save('calibration-checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=True,anchors=checks,dense_controls=grid,ledger=ledger,source_or_target_images_read=0));print('CALIBRATION PASS',checks,flush=True)
except Exception as e:save('calibration-failure.json',dict(error=repr(e),traceback=traceback.format_exc(),ledger=ledger));raise
finally:save('calibration-ledger.json',ledger)
