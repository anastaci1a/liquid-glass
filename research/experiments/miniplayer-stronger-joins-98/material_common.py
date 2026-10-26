"""Read-only fixed evidence loader and original scoring for separate effects."""
from pathlib import Path
import ast,json,hashlib,datetime,zipfile,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
F=json.loads((ROOT/'reconstruction/families/music-mini-player-working.json').read_text());L=F['length_unit_native_pixels']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load_data(charge,first):
 data={}
 def read(p,keys):
  first[str(p.relative_to(ROOT))]=sha(p)
  with zipfile.ZipFile(p) as z:
   for k in keys:
    with z.open(k+'.npy') as f:
     v=np.lib.format.read_magic(f);shape,_,dt=(np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f));assert not dt.hasobject;charge('numeric_bytes',int(np.prod(shape))*dt.itemsize)
  with np.load(p) as z:return {k:z[k] for k in keys}
 # Complete previously reviewed constructor inventory, excluding comparison PNGs.
 inv=json.loads((ROOT/'research/experiments/agent-outline-series-replay-57/headers-and-decode-reservation.json').read_text())
 for r in inv['bitmaps']:
  if r['role']=='Final saved comparison inspection':continue
  charge('bitmap_pixels',r['pixels'])
 for r in json.loads((ROOT/'research/experiments/agent-outline-series-replay-57/foreground-assets-review.json').read_text())['assets']:
  p=ROOT/r['file'];assert sha(p)==r['sha256'];first[r['file']]=r['sha256']
 for member in ['expanded','compact']:
  work=ROOT/f'.evidence-working/{member}-geometry-0{2 if member=="expanded" else 1}'
  center=np.array(json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])
  if member=='compact':
   pr=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];case=json.loads((work/'a/case.json').read_text());center=np.array(case['center'])+L*np.array([pr['shape_dx'],pr['shape_dy']])
  half=np.array([F['members'][member]['major_half'],F['geometry']['minor_half']])*L;radius=F['geometry']['corner_radius']*L
  for k in ['a','b']:
   cp=work/k/'case.json';first[str(cp.relative_to(ROOT))]=sha(cp);case=json.loads(cp.read_text())
   for fn,h in case['source_sha256'].items():assert sha(work/k/fn)==h;first[str((work/k/fn).relative_to(ROOT))]=h
   charge('Studies',1);s=Study(work/k);charge('mask_points',s.valid.size)
   p=BASE/f'native/{member}-{k}-geometry.npz';z=read(p,['complete','pre_foreground','encoded_subrays','raw_source','inside','coverage','supported'])
   mp=work/f'{k}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz';m=read(mp,['glass','rim','held','exterior'])
   old=read(ROOT/f'research/experiments/miniplayer-incident-material-20/{member}-{k}-factor0.5.npz',['complete','coverage'])
   cov=old['coverage'] if member=='expanded' else read(ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz',['coverage'])['coverage']
   partial=m['glass']&(cov<1);assert partial.sum()==(16 if member=='expanded' else 22)
   assert np.array_equal(s.valid,m['glass']) and np.array_equal(s.rim,m['rim']) and np.array_equal(s.held,m['held'])
   metric=json.loads((BASE/f'native/{member}-{k}-geometry-metrics.json').read_text())
   crops=json.loads((ROOT/'research/experiments/miniplayer-inverse-forward-18/protocol.json').read_text())['fixed_crops'][member]
   train=m['glass']&~m['held'];x0,y0,_,_=s.crop
   for layer in s.case['foreground_layers']:
    a,b,c,e=layer['box'];assert not train[b-y0:e-y0,a-x0:c-x0].any()
   data[(member,k)]=dict(s=s,z=z,m=m,partial=partial,old=old['complete'],before=metric['scores'],original=metric['baseline'],crops=crops,center=center,half=half,radius=radius,train=train)
 return data

def metric_functions(charge):
 p=ROOT/'research/experiments/miniplayer-outline-light-07/render.py';t=ast.parse(p.read_text());ns={'np':np,'Image':Image,'charge':charge};exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in ['score','display','to_image']],type_ignores=[]),str(p),'exec'),ns);return ns

def guards(now,before):
 z={k:now[k]['rmse']<=before[k]['rmse'] for k in ['glass','rim','held','interior']};z.update(E=now['E']<=before['E'],SSIM=now['ssim']>=before['ssim'],exterior=now['exterior']<=before['exterior'],partial=now['partial']['RMSE']<=before['partial']['RMSE']);z.update({k:v<=before['foreground'][k] for k,v in now['foreground'].items()});return z

def panels(out,prefix,d,C,to_image,label):
 H,W=C.shape[:2];sheet=Image.new('RGB',(3*W+4,H+38),'white');draw=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=16)
 for i,(v,title) in enumerate([(d['s'].target_crop,'Reference'),(d['old'],'Original working20'),(C,label)]):sheet.paste(to_image(v),(i*(W+2),38));draw.text((i*(W+2)+4,8),title,font=font,fill='black')
 sheet.save(out/f'{prefix}-comparison.png')
 rows=[];x0,y0,_,_=d['s'].crop
 for name,(a,b,c,e) in d['crops'].items():
  w,h=(c-a)*3,(e-b)*3;row=Image.new('RGB',(3*w+4,h+28),'white');rd=ImageDraw.Draw(row)
  for i,v in enumerate([d['s'].target_crop,d['old'],C]):row.paste(to_image(v[b-y0:e-y0,a-x0:c-x0]).resize((w,h),Image.Resampling.NEAREST),(i*(w+2),28))
  rd.text((4,5),name,font=font,fill='black');rows.append(row)
 sheet=Image.new('RGB',(max(r.width for r in rows),sum(r.height for r in rows)),'white');y=0
 for row in rows:sheet.paste(row,(0,y));y+=row.height
 sheet.save(out/f'{prefix}-crops.png')
