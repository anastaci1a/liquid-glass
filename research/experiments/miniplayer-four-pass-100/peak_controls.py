from pathlib import Path
import numpy as np,json,datetime,traceback
from miniplayer_refinement_effects import peak_preserving_rim
P=Path(__file__).parent/'pass2';maximum=2048;count=0;records=[]
(P/'response-control-start.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'maximum_color_inputs':maximum,'optical_calls':0},indent=2)+'\n')
try:
 a=np.array([0.,.001,.1,.5,.9,1.]);colors=np.stack(np.meshgrid(a,a,a),-1).reshape(-1,3)
 for chroma in [1.,1.25,1.5]:
  for alpha in [0.,.5,1.]:
   count+=len(colors);assert count<=maximum
   out=peak_preserving_rim(colors,colors,np.full(len(colors),alpha),chroma)
   assert np.isfinite(out).all() and out.min()>=0 and out.max()<=1
   if alpha==0:assert np.array_equal(out,colors)
   white=np.all(colors==1,axis=1);assert np.array_equal(out[white],colors[white]);records.append(dict(chroma=chroma,alpha=alpha,minimum=float(out.min()),maximum=float(out.max())))
 black=np.zeros((1,3));near=np.eye(3)*1e-9;count+=4;assert count<=maximum;b=peak_preserving_rim(black,black,np.ones(1));n=peak_preserving_rim(near,near,np.ones(3));assert np.max(abs(n-b))<1e-7
 (P/'response-controls.json').write_text(json.dumps({'passed':True,'color_inputs':count,'black_endpoint':b[0].tolist(),'near_black_continuity_error':float(np.max(abs(n-b))),'records':records},indent=2)+'\n');print('PEAK RESPONSE CONTROLS PASS',count,b)
except Exception as e:(P/'response-controls-failure.json').write_text(json.dumps({'error':repr(e),'traceback':traceback.format_exc(),'color_inputs':count},indent=2)+'\n');raise
