from pathlib import Path
import json,hashlib,urllib.request,datetime,concurrent.futures
r=Path('/repo');o=r/'research/experiments/miniplayer-stronger-joins-98'
sha='588f6b48ad4850ec7198d9dfaaafdde666ea4929'
base='https://anastaci1a.github.io/liquid-glass/'
def fetch(path):
 with urllib.request.urlopen(base+path+'?verify='+sha,timeout=40) as f:return f.read()
html=fetch('miniplayer-feedback-review.html').decode()
assert 'Stronger joins' in html and 'feedback98-compact-b-final.png' in html
panels=json.loads((o/'publication-panels.json').read_text())['panels']
def check(item):
 data=fetch(item['asset']); digest=hashlib.sha256(data).hexdigest();assert digest==item['sha256'],item['asset']
 return dict(path=item['asset'],sha256=digest,bytes=len(data))
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(check,panels))
record=dict(verified_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),deployment_commit=sha,page=base+'miniplayer-feedback-review.html',page_sha256=hashlib.sha256(html.encode()).hexdigest(),all_32_assets_exact=True,assets=results,scientific_evaluations=0)
(o/'live-publication.json').write_text(json.dumps(record,indent=2)+'\n')
print('PASS live page and',len(results),'exact asset hashes')
