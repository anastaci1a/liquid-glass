from pathlib import Path
import numpy as np,json,datetime,hashlib
from miniplayer_refinement_effects import soft_channel_rim,soft_channel_rim_dark,low_luminance_body
O=Path(__file__).parent/'pass4';start=datetime.datetime.now(datetime.timezone.utc)
(O/'response-controls-start.json').write_text(json.dumps(dict(start=start.isoformat(),cap=20000,scope='Fixed synthetic unit cube, white, black, zero-alpha and low-luminance lift controls; no target/source samples'),indent=2))
grid=np.stack(np.meshgrid(*([np.linspace(0,1,9)]*3),indexing='ij'),-1).reshape(-1,3);count=0;records=[]
for power in [0,.12,.24]:
 for body in [grid, np.ones_like(grid),np.zeros_like(grid)]:
  C=soft_channel_rim_dark(body,grid,np.ones(len(grid)),1.75,power);count+=len(grid);assert np.isfinite(C).all() and C.min()>=0 and C.max()<=1+1e-12
  if np.all(body==1):assert np.array_equal(C,body)
  assert np.array_equal(soft_channel_rim_dark(body,grid,np.zeros(len(grid)),1.75,power),body);count+=len(grid)
 records.append(dict(dark_neutral=power,black_endpoint=soft_channel_rim_dark(np.zeros((1,3)),np.zeros((1,3)),np.ones(1),1.75,power).tolist()))
for t in [.04,.08,.12]:
 C=low_luminance_body(grid,.5552987769129158,.39083683534488656,t);count+=len(grid);assert C.min()>=0 and C.max()<=1
 assert np.array_equal(C[-1],np.ones(3)*(.5552987769129158+.39083683534488656))
count+=3
assert np.array_equal(soft_channel_rim_dark(grid,grid,np.ones(len(grid)),1.75,0),soft_channel_rim(grid,grid,np.ones(len(grid)),1.75));count+=2*len(grid)
assert count<=20000
(O/'response-controls.json').write_text(json.dumps(dict(passed=True,synthetic_inputs=count,records=records,finished=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
print('RESPONSE CONTROLS PASS',count)
