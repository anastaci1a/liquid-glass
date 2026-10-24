"""Synthetic accounting tests only; do not import or execute optical definitions."""
import ast,copy,datetime,hashlib,json,types
from pathlib import Path
import numpy as np
from combined_callback import Counter,SCHEMA
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
P=json.loads((OUT/'protocol.json').read_text())
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def clock():
 if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00')):raise RuntimeError('Deadline')
assert not (OUT/'synthetic-result.json').exists(),'No silent rerun'
source=(ROOT/'reconstruction/geometric_optics.py').read_bytes()
old=(ROOT/'research/experiments/agent-membership-parity-13/check.py').read_bytes()
assert hashlib.sha256(source).hexdigest()==P['shared_sha256']
assert hashlib.sha256(old).hexdigest()==P['old_driver_sha256']
# Parsing and compilation create code objects only; neither module is imported or executed.
tree=ast.parse(source);compiled=compile(tree,'pinned-geometric-optics.py','exec')
selected={'HarmonicCircularBack','CircularHeightSolid'}
inventory=[]
for node in tree.body:
 if isinstance(node,(ast.FunctionDef,ast.ClassDef)):
  if isinstance(node,ast.ClassDef) and node.name in selected:
   for method in node.body:
    if isinstance(method,ast.FunctionDef):inventory.append({'owner':node.name,'name':method.name,'line':method.lineno,'calls':sorted({ast.unparse(c.func) for c in ast.walk(method) if isinstance(c,ast.Call)})})
  elif isinstance(node,ast.FunctionDef) and (None,node.name) in SCHEMA:
   inventory.append({'owner':None,'name':node.name,'line':node.lineno,'calls':sorted({ast.unparse(c.func) for c in ast.walk(node) if isinstance(c,ast.Call)})})
(OUT/'static-definitions.json').write_text(json.dumps({'compiled_not_executed':True,'definitions':inventory,'generated_constructor':'Dataclass __init__ has <string> filename; explicitly included by selected owner/name, not imported or constructed here.'},indent=2)+'\n')
rows=np.zeros(33);vectors=np.zeros((33,3));small=np.zeros(25)
classes={name:type(name,(),{}) for name in ('ScaledFlatBack','HarmonicCircularBack','CircularHeightSolid')}
def frame(owner,name,values=None,filename='core',qualname=None):
 v={} if values is None else dict(values)
 if owner:v['self']=classes[owner]()
 return types.SimpleNamespace(f_code=types.SimpleNamespace(co_filename=filename,co_name=name,co_qualname=qualname or name),f_locals=v)
def vals(rule):
 return {'scalar':{},'xy':{'x':rows,'y':rows},'rho':{'rho':rows},'harmonic_pair':{'first':rows,'second':rows},'vector_pair':{'incident':vectors,'against_incident_normal':vectors},'segment_pair':{'points':vectors,'directions':vectors},'points':{'p':vectors},'points_uncertainty':{'p':vectors,'uncertainty':rows},'metadata':{'v':rows,'shape':(33,)}}[rule]
records=[]
def test(label,f,c=None,want=None,reject=False,event='call'):
 clock()
 if len(records)>=64:raise RuntimeError('Synthetic fixture cap')
 c=c or Counter('core','adapter');before=copy.deepcopy(c.ledger)
 rec={'number':len(records)+1,'label':label};records.append(rec)
 try:c(f,event,None)
 except (ValueError,RuntimeError) as exc:
  if not reject:raise
  assert c.ledger==before,'Rejected call mutated ledger'
  rec.update(status='PASS_EXPECTED_REJECTION',reason=str(exc),ledger_unchanged=True);return
 assert not reject,'Expected rejection did not occur'
 assert c.ledger['total']-before['total']==want
 rec.update(status='PASS',charged=want)
try:
 for (owner,name),(rule,category) in SCHEMA.items():
  if name in ('reflect_direction','fresnel_components'):continue
  filename='adapter' if owner=='ScaledFlatBack' else ('<string>' if owner=='HarmonicCircularBack' and name=='__init__' else 'core')
  f=frame(owner,name,vals(rule),filename,'trace_closed_orthographic.<locals>.<lambda>' if name=='<lambda>' else None)
  test((owner or 'module')+'.'+name,f,want=1 if rule=='scalar' else 33)
 test('vector metadata',frame(None,'<lambda>',{'v':vectors,'shape':(33,)},qualname='trace_closed_orthographic.<locals>.<lambda>'),want=33)
 test('25-row delegate',frame(None,'bevel_profile',{'rho':small}),want=25)
 test('unknown shared call before hypothetical body',frame(None,'undeclared_delegate',{}),reject=True)
 test('unknown generated method',frame('HarmonicCircularBack','__repr__',{},'<string>'),reject=True)
 test('unknown metadata lambda',frame(None,'<lambda>',{'v':rows,'shape':(33,)}),reject=True)
 test('mismatched xy',frame(None,'trace_flat_front_orthographic',{'x':rows,'y':small}),reject=True)
 test('mismatched harmonic',frame(None,'harmonic_cap',{'first':rows,'second':small}),reject=True)
 test('mismatched refract vectors',frame(None,'refract',{'incident':vectors,'against_incident_normal':np.zeros((25,3))}),reject=True)
 test('mismatched segment vectors',frame(None,'next_convex_boundary',{'points':vectors,'directions':np.zeros((25,3))}),reject=True)
 test('scalar rho not claimed',frame(None,'bevel_profile',{'rho':0.}),reject=True)
 test('matrix rho not claimed',frame(None,'bevel_profile',{'rho':vectors}),reject=True)
 test('bad metadata output shape',frame(None,'<lambda>',{'v':vectors,'shape':(25,)},qualname='trace_closed_orthographic.<locals>.<lambda>'),reject=True)
 test('bad uncertainty shape',frame('CircularHeightSolid','nonsmooth_mask',{'p':vectors,'uncertainty':small}),reject=True)
 test('global nested rejection',frame(None,'bevel_profile',{'rho':rows}),Counter('core','adapter',global_cap=32),reject=True)
 test('per-config nested rejection',frame(None,'bevel_profile',{'rho':rows}),Counter('core','adapter',config_cap=32),reject=True)
 test('global level rejection',frame('CircularHeightSolid','level_gradient',{'p':vectors}),Counter('core','adapter',level_cap=32),reject=True)
 test('per-config level rejection',frame('CircularHeightSolid','level_gradient',{'p':vectors}),Counter('core','adapter',config_level_cap=32),reject=True)
 test('exact cap accepted once',frame('CircularHeightSolid','level_gradient',{'p':vectors}),Counter('core','adapter',global_cap=33,level_cap=33,config_cap=33,config_level_cap=33),want=33)
 c=Counter('core','adapter');c.ledger['total']=99999;c.start_total=99999
 test('nonzero global ledger rejection',frame(None,'bevel_profile',{'rho':rows}),c,reject=True)
 c=Counter('core','adapter');c.ledger['total']=15000;c.start_total=0
 test('nonzero config ledger rejection',frame(None,'bevel_profile',{'rho':rows}),c,reject=True)
 test('return event ignored',frame(None,'bevel_profile',{'rho':rows}),want=0,event='return')
 test('unrelated module ignored',frame(None,'unknown',{},'outside'),want=0)

 assert len(records)==46,'Old regression suite changed'
 newstart=len(records)
 for n in (1,16):
  v=np.zeros((n,3));test('primitive reflect '+str(n),frame(None,'reflect_direction',{'incident':v,'outward_normal':v}),want=n)
 for n in (1,16):
  co=np.zeros(n);test('primitive Fresnel '+str(n),frame(None,'fresnel_components',{'cosine':co,'n_from':1.5,'n_to':1.}),want=n)
 test('primitive mismatched reflect',frame(None,'reflect_direction',{'incident':np.zeros((1,3)),'outward_normal':np.zeros((16,3))}),reject=True)
 test('primitive rank reflect',frame(None,'reflect_direction',{'incident':np.zeros(3),'outward_normal':np.zeros(3)}),reject=True)
 test('primitive scalar cosine',frame(None,'fresnel_components',{'cosine':0.,'n_from':1.5,'n_to':1.}),reject=True)
 test('primitive matrix cosine',frame(None,'fresnel_components',{'cosine':np.zeros((1,3)),'n_from':1.5,'n_to':1.}),reject=True)
 test('primitive array index',frame(None,'fresnel_components',{'cosine':np.zeros(1),'n_from':np.zeros(1),'n_to':1.}),reject=True)
 test('primitive forbidden unpolarized',frame(None,'fresnel_unpolarized',{}),reject=True)
 c=Counter('core','adapter',global_cap=16);c.ledger['total']=1;c.ledger['categories']={'interface':1};c.ledger['functions']={'prior_interface':1}
 test('primitive global mixed guard',frame(None,'reflect_direction',{'incident':np.zeros((16,3)),'outward_normal':np.zeros((16,3))}),c,reject=True)
 test('primitive exact cap Fresnel',frame(None,'fresnel_components',{'cosine':np.zeros(16),'n_from':1.5,'n_to':1.}),Counter('core','adapter',global_cap=16),want=16)
 assert len(records)-newstart==12
 for bad in (float('nan'),float('inf'),0.,-1.):
  test('finite-positive index rejection '+str(bad),frame(None,'fresnel_components',{'cosine':np.zeros(1),'n_from':bad,'n_to':1.}),reject=True)
 mixed=Counter('core','adapter',config_cap=11)
 mixed.ledger={'total':10,'closed_level_subset':1,'categories':{'point_queries':9,'closed_level':1},'functions':{'old_height_query':9,'old_level_query':1}}
 test('combined reflection shares seeded query total',frame(None,'reflect_direction',{'incident':np.zeros((1,3)),'outward_normal':np.zeros((1,3))}),mixed,want=1)
 assert mixed.ledger['total']==11 and mixed.ledger['closed_level_subset']==1 and mixed.ledger['categories']['interface']==1
 test('combined Fresnel per-launch guard preserves full mixed ledger',frame(None,'fresnel_components',{'cosine':np.zeros(1),'n_from':1.5,'n_to':1.}),mixed,reject=True)
 assert len(records)==64
 status='PASS_COMBINED_SYNTHETIC_ONLY'
except Exception as e:
 status='FAIL_STOP';failure=repr(e)
result={'status':status,'finished':now(),'fixtures':len(records),'fixture_cap':64,'records':records,'shared_module_imported':False,'shared_code_compiled_but_executed':False,'real_profiler_installed':False,'optical_evaluations':0,'source_arrays_read':0,'maximum_placeholder_shape':[33,3]}
if status!='PASS_COMBINED_SYNTHETIC_ONLY':result['failure']=failure
(OUT/'synthetic-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':status,'fixtures':len(records),'failure':result.get('failure')}))
