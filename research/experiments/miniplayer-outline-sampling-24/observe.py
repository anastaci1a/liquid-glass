"""Fixed local quadrature diagnostic. No optical parameter or scoring epoch change."""
from pathlib import Path
import sys,json,datetime,ast
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;A=ROOT/'research/experiments/miniplayer-inverse-forward-18';B=ROOT/'research/experiments/miniplayer-narrow-emitter-22';M=ROOT/'research/experiments/miniplayer-incident-material-20'
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']}
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def gate():assert datetime.datetime.now(datetime.timezone.utc)<END,'Original diagnostic deadline'
def charge(k,n):
 gate();assert ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n);save('ledger.json',ledger)
def count(label,n):charge('surface_point_queries',n);charge('conservative_adapter_units',20*n)
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from music_miniplayer_family import load_family,surface_for_member
from hermite_height_back import HermiteFootprintBack
from raised_front_optics import VerticalScaleBack,trace_raised_front_orthographic
from geometric_render import neutral_color_response,incident_source_filter
from environment_radiance import annular_environment,decode_srgb,encode_srgb
cv2.setNumThreads(1);F=load_family();L=F['length_unit_native_pixels'];model=json.loads((ROOT/'research/experiments/miniplayer-inverse-geometry-17/back-profile.json').read_text());tree=ast.parse((ROOT/'research/experiments/miniplayer-outline-light-07/render.py').read_text());defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['display','to_image']];exec(compile(ast.Module(body=defs,type_ignores=[]),'display-only','exec'))
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});data={};check=[];layouts={}
for member in ['expanded','compact']:
 base=surface_for_member(member);work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01');oldq=np.load(A/f'{member}-paths.npz');entries=[]
 for ref in ['a','b']:
  charge('Study_constructor_pixels',1360*250 if member=='expanded' else 920*240);s=Study(work/ref);case=dict(s.case)
  if member=='expanded':case['center']=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center']
  else:
   prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];case['center']=(np.asarray(case['center'])+s.L*np.array([prior['shape_dx'],prior['shape_dy']])).tolist()
  cx,cy=case['center'];centers=[('left_cap',cx-base.half[0]*L,cy),('right_cap',cx+base.half[0]*L,cy),('upper_straight',cx,cy-base.half[1]*L),('lower_straight',cx,cy+base.half[1]*L)];tiles=[]
  raw=np.load(A/f'{member}-{ref}-light4.npz')['raw_source'];old=np.load(B/f'{member}-{ref}.npz');mat=json.loads((M/f'{member}-{ref}-factor0.5-metrics.json').read_text());m=np.load(work/f'{ref}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{ref}-masks.npz');assert np.array_equal(m['glass'],s.valid)
  x0,y0,x1,y1=s.crop
  for name,x,y in centers:
   a,b=int(round(x))-16,int(round(y))-12;c,d=a+32,b+24;assert x0<=a<c<=x1 and y0<=b<d<=y1
   assert not any(max(a,u)<min(c,w) and max(b,v)<min(d,z) for layer in s.case['foreground_layers'] for u,v,w,z in [layer['box']]),'Foreground tile overlap'
   yy=slice(b-y0,d-y0);xx=slice(a-x0,c-x0);ys=slice(2*(b-y0),2*(d-y0));xs=slice(2*(a-x0),2*(c-x0));inside=oldq['inside'][ys,xs];sample=raw[ys,xs].copy();primary=neutral_color_response(sample[inside],gain=mat['gain'],bias=mat['bias']);charge('scene_direction_queries',int(inside.sum()));unit=oldq['front_reflection_power'][ys,xs][inside]*annular_environment(oldq['front_reflection_direction'][ys,xs][inside],36,44,.5);sample[inside]=np.clip(encode_srgb(oldq['primary_power'][ys,xs][inside,None]*decode_srgb(primary)+8*unit[:,None]),0,1);pre=sample.reshape(24,2,32,2,3).mean((1,3)).astype(np.float32);charge('cached_identity_tiles',1);assert np.array_equal(pre,old['pre_foreground'][yy,xx],equal_nan=True) and np.array_equal(pre,old['complete'][yy,xx],equal_nan=True),'Cached tile identity'
   tiles.append(dict(name=name,box=[a,b,c,d],baseline=pre.copy(),target=s.target_crop[yy,xx].copy(),glass=m['glass'][yy,xx].copy(),required=(m['glass']|m['rim']|m['held']|m['exterior'])[yy,xx].copy()))
  known=cv2.imread(str(work/ref/'known.png'),0)>0;entries.append(dict(s=s,case=case,tiles=tiles,known=known,material=mat,reference=ref));check.append({'member':member,'reference':ref,'four_cached_tiles_exact':True,'foreground_overlap':0})
 assert entries[0]['case']['center']==entries[1]['case']['center'];data[member]=entries;layouts[member]=[{'name':t['name'],'box':t['box']} for t in entries[0]['tiles']]
save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':check,'tile_layouts':layouts,'new_rays':0,'ledger':ledger});paths={};proof=[]
for member,entries in data.items():
 base=surface_for_member(member);charge('profile_bound_segments',len(model['heights'])-1);back=HermiteFootprintBack(base,model);front=VerticalScaleBack(base,.5);xx=[];yy=[];center=entries[0]['case']['center']
 for t in entries[0]['tiles']:
  a,b,c,d=t['box'];Y,X=np.mgrid[b:d:.25,a:c:.25];xx.append((X-.375-center[0])/L);yy.append((Y-.375-center[1])/L)
 X,Y=np.stack(xx),np.stack(yy);charge('native_rays',X.size);q=trace_raised_front_orthographic(back,X,Y,1.,1.5,2.1,count,front_surface=front);assert q['complete'].all();paths[member]=q;np.savez_compressed(OUT/f'{member}-paths-AA4.npz',**q)
 SX=q['X']*L+center[0];SY=q['Y']*L+center[1];aa=np.floor(SX).astype(int);bb=np.floor(SY).astype(int);inside=q['inside'];charge('scene_direction_queries',int(inside.sum()));unit=np.zeros(inside.shape);unit[inside]=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside],36,44,.5)
 for e in entries:
  known=e['known'];charge('known_erosions',1);safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0;bounds=np.isfinite(SX)&np.isfinite(SY)&(aa>=0)&(bb>=0)&(aa+1<known.shape[1])&(bb+1<known.shape[0]);ii=np.nonzero(bounds);rawok=np.zeros_like(bounds);blur=np.zeros_like(bounds)
  for out,mask in [(rawok,known),(blur,safe)]:
   charge('bilinear_known_lookups',4*len(ii[0]));out[ii]=mask[bb[ii],aa[ii]]&mask[bb[ii]+1,aa[ii]]&mask[bb[ii],aa[ii]+1]&mask[bb[ii]+1,aa[ii]+1]
  supported=np.where(inside,blur,rawok);required=inside|np.stack([np.repeat(np.repeat(t['required'],4,0),4,1) for t in e['tiles']]);charge('source_audit_subrays',X.size);assert not (required&~supported).any(),'Required AA4 source unsupported';proof.append({'member':member,'reference':e['reference'],'whole':int(inside.sum()),'required':int(required.sum()),'unsupported_required':0,'unknown_unscored':int((~supported&~required).sum()),'RGB_queries':0});e.update(supported=supported,safe=safe,aa=aa,bb=bb,SX=SX,SY=SY,unit=unit)
save('source-FIRST.json',{'status':'ALL_FOUR_GATES_PASS_BEFORE_FIELDS_OR_RGB','records':proof});records=[]
for member,entries in data.items():
 q=paths[member];inside=q['inside']
 for e in entries:
  charge('incident_fields',1);charge('known_erosions',1);field,safe,r=incident_source_filter(e['s'].source,e['known'],6.75);assert r==21 and np.array_equal(safe,e['safe']);raw=np.full(inside.shape+(3,),np.nan)
  for select,source in [(inside,field),(~inside&e['supported'],e['s'].source)]:
   ids=np.nonzero(select);charge('RGB_queries',len(ids[0]));a=e['aa'][ids];b=e['bb'][ids];wx=(e['SX'][ids]-a)[:,None];wy=(e['SY'][ids]-b)[:,None];raw[ids]=(source[b,a]*(1-wx)+source[b,a+1]*wx)*(1-wy)+(source[b+1,a]*(1-wx)+source[b+1,a+1]*wx)*wy
  mat=e['material'];primary=neutral_color_response(raw[inside],gain=mat['gain'],bias=mat['bias']);raw[inside]=np.clip(encode_srgb(q['primary_power'][inside,None]*decode_srgb(primary)+8*e['unit'][inside,None]),0,1);C=raw.reshape(4,24,4,32,4,3).mean((2,4)).astype(np.float32);prefix=f'{member}-{e["reference"]}';np.savez_compressed(OUT/f'{prefix}-tiles-AA4.npz',AA4=C,AA2=np.stack([t['baseline'] for t in e['tiles']]),target=np.stack([t['target'] for t in e['tiles']]))
  rows=[];font=ImageFont.load_default(size=12)
  for i,t in enumerate(e['tiles']):
   charge('new_tile_integrations',1);mask=t['glass'];err2=(t['baseline']-t['target'])*255;err4=(C[i]-t['target'])*255;assert np.isfinite(C[i][mask]).all();record={'member':member,'reference':e['reference'],'tile':t['name'],'original_glass_pixels':int(mask.sum()),'AA2_RMSE':float(np.sqrt(np.mean(err2[mask]**2))),'AA4_RMSE':float(np.sqrt(np.mean(err4[mask]**2))),'AA2_MAE':float(np.mean(abs(err2[mask]))),'AA4_MAE':float(np.mean(abs(err4[mask])))};records.append(record);row=Image.new('RGB',(196,84),'white');draw=ImageDraw.Draw(row);draw.text((2,0),t['name'],fill='black',font=font)
   for j,(v,label) in enumerate([(t['target'],'Reference'),(t['baseline'],'AA2'),(C[i],'AA4')]):row.paste(to_image(v).resize((64,48),Image.Resampling.NEAREST),(j*66,36));draw.text((j*66,18),label,fill='black',font=font)
   rows.append(row)
  sheet=Image.new('RGB',(196,4*88-4),'white')
  for i,row in enumerate(rows):sheet.paste(row,(0,88*i))
  sheet.save(OUT/f'{prefix}-sampling-2x.png')
save('result.json',{'status':'LOCAL_SAMPLING_DIAGNOSTIC_COMPLETE_NO_OPTICAL_ADOPTION','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'AA2_protocol_unchanged':True,'full_image_scores':False,'adopted':False})
