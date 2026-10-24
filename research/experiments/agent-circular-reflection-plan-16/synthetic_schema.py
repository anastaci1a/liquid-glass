"""Only synthetic new-dispatch tests, with no shared optical import or body."""
import json,types,datetime
from pathlib import Path
import numpy as np
from schema_proposal import charge_synthetic
P=Path(__file__).resolve().parent
assert not (P/'synthetic-result.json').exists()
protocol=json.loads((P/'protocol.json').read_text())
records=[]
def test(name,local,expected=None,reject=False,initial=0,limit=100):
 assert len(records)<16
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(protocol['deadline'].replace('Z','+00:00'))
 ledger={'interface':initial};frame=types.SimpleNamespace(f_code=types.SimpleNamespace(co_name=name),f_locals=local)
 before=dict(ledger)
 try:n=charge_synthetic(frame,ledger,limit)
 except (ValueError,RuntimeError) as e:
  assert reject and ledger==before
  records.append({'name':name,'status':'PASS_EXPECTED_REJECTION','reason':str(e),'ledger_unchanged':True});return
 assert not reject and n==expected and ledger['interface']==initial+expected
 records.append({'name':name,'status':'PASS','units':n})
v1=np.zeros((1,3));v16=np.zeros((16,3));c1=np.zeros(1);c16=np.zeros(16)
for v in (v1,v16):test('reflect_direction',{'incident':v,'outward_normal':v},len(v))
for c in (c1,c16):test('fresnel_components',{'cosine':c,'n_from':1.5,'n_to':1.},len(c))
test('reflect_direction',{'incident':v1,'outward_normal':v16},reject=True)
test('reflect_direction',{'incident':np.zeros(3),'outward_normal':np.zeros(3)},reject=True)
test('fresnel_components',{'cosine':0.,'n_from':1.5,'n_to':1.},reject=True)
test('fresnel_components',{'cosine':v1,'n_from':1.5,'n_to':1.},reject=True)
test('fresnel_components',{'cosine':c1,'n_from':np.zeros(1),'n_to':1.},reject=True)
test('fresnel_unpolarized',{},reject=True)
test('reflect_direction',{'incident':v16,'outward_normal':v16},reject=True,initial=1,limit=16)
test('fresnel_components',{'cosine':c16,'n_from':1.5,'n_to':1.},16,limit=16)
(P/'synthetic-result.json').write_text(json.dumps({'status':'PASS_SYNTHETIC_DISPATCH_ONLY','fixtures':len(records),'cap':16,'records':records,'shared_imports':0,'shared_function_body_calls':0,'real_profiler_installations':0},indent=2)+'\n')
print(json.dumps({'status':'PASS_SYNTHETIC_DISPATCH_ONLY','fixtures':len(records)}))
