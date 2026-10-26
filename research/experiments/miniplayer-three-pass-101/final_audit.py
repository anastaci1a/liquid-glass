"""Saved-record integrity and categorized accounting; no array reductions."""
from pathlib import Path
import json,hashlib,datetime
B=Path(__file__).parent;start=datetime.datetime.now(datetime.timezone.utc);end=start+datetime.timedelta(minutes=10);used=0;cap=50_000_000_000;rows=[]
def digest(p):
 global used
 h=hashlib.sha256()
 with p.open('rb') as f:
  while chunk:=f.read(1024*1024):
   used+=len(chunk);assert used<=cap and datetime.datetime.now(datetime.timezone.utc)<end;h.update(chunk)
 return h.hexdigest()
(B/'audit-start.json').write_text(json.dumps(dict(start=start.isoformat(),deadline=end.isoformat(),maximum_hashed_bytes=cap,numerical_evaluations=0),indent=2)+'\n')
for base,folders in [(B.parent/'miniplayer-four-pass-100',[f'pass{i}' for i in range(1,5)]),(B,['pass1','pass2','pass3','native-pass1','native-pass1-corrected','native-pass2-corrected','native-pass2-resumed','native-pass3-corrected'])]:
 for name in folders:
  p=base/name;v=json.loads((p/'manifest.json').read_text());entries=v.get('files',v);payload=pointer=0
  for rel,expected in entries.items():
   f=p/rel
   if f.stat().st_size<200 and f.suffix=='.npz' and f.read_bytes().startswith(b'version https://git-lfs.github.com/spec/v1'):
    assert ('oid sha256:'+expected) in f.read_text();pointer+=1
   else:assert digest(f)==expected,str(f);payload+=1
  rows.append(dict(folder=str(p.relative_to(B.parents[2])),payload_hashes_verified=payload,pointer_identities_only=pointer))
ledgers={}
for name in ['native-pass1','native-pass1-corrected','native-pass2-corrected','native-pass2-resumed','native-pass3-corrected']:ledgers[name]=json.loads((B/name/'native-ledger.json').read_text())
charged_native=sum(v['geometry_cumulative']['native_rays'] for v in ledgers.values())+87040
for n in range(1,4):
 p=B/f'pass{n}';ledgers[f'pass{n}-display']=json.loads((p/'ledger.json').read_text());ledgers[f'pass{n}-own-review']=json.loads((p/'verification.json').read_text())['ledger']
record=dict(finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),manifest_reviews=rows,hashed_bytes=used,charged_native_launch_attempts=charged_native,storage_failed_unretained_batch_supplement=87040,full_successful_native_grids=3,reused_native_records=783360,unknown_accounting='Second-pass failed storage batch has unknown nested usage beyond its durable ledger; the original caps remain conservative bounds. No exact cumulative nested total is asserted.',ledgers=ledgers,numerical_evaluations=0)
(B/'final-integrity-and-ledgers.json').write_text(json.dumps(record,indent=2)+'\n');print('INTEGRITY PASS',sum(r['payload_hashes_verified'] for r in rows),'payloads; charged native attempts',charged_native)
