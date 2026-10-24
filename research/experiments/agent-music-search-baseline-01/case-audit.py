from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[2]
a=json.loads((R/'reconstruction/studies/music-search-vector/review-round/pass-03-verification.json').read_text())['protocol']['cases'];rows=[]
def types(x,y,path=''):
 out=[]
 if type(x)!=type(y):out.append(dict(path=path,original_type=type(x).__name__,intake_type=type(y).__name__,original_value=x,intake_value=y))
 if isinstance(x,dict) and isinstance(y,dict):
  for k in x.keys()&y.keys():out+=types(x[k],y[k],path+'/'+k)
 elif isinstance(x,list) and isinstance(y,list):
  for i,(v,w) in enumerate(zip(x,y)):out+=types(v,w,path+'/'+str(i))
 return out
for k,orig in zip(['a','b'],a):
 frozen=json.loads((P/'cases'/f'{k}.json').read_text());rows.append(dict(case=k,original_verification_case_fingerprint=hashlib.sha256(json.dumps(orig,sort_keys=True).encode()).hexdigest(),semantic_equal=orig==frozen,type_differences=types(orig,frozen),original_keys=sorted(orig),intake_keys=sorted(frozen)))
(P/'case-audit.json').write_text(json.dumps(dict(status='SEMANTIC_AND_TYPE_AUDIT_ONLY',rows=rows),indent=2)+'\n');print(json.dumps(rows))
