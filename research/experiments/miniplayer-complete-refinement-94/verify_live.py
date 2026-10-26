"""Verify deployed report and every exact-pair asset against committed bytes."""
from pathlib import Path
import json,hashlib,urllib.request,datetime,concurrent.futures,subprocess
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent;URL='https://anastaci1a.github.io/liquid-glass/'
expected=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
def get(path):
 with urllib.request.urlopen(URL+path+'?check='+expected,timeout=45) as r:return r.read()
html=get('miniplayer-refinement.html').decode();assert expected[:8] in html,'Deployment has not reached expected commit';assert html.count('data-comparison-top=')==64
bindings=json.loads((BASE/'presentation-bindings.json').read_text())['assets']
def one(row):
 raw=get(row['asset']);h=hashlib.sha256(raw).hexdigest();assert h==row['sha256'],row['asset'];return {'asset':row['asset'],'sha256':h,'bytes':len(raw)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:assets=list(pool.map(one,bindings))
for path in ['research/experiments/miniplayer-complete-refinement-94/index.html','research/experiments/miniplayer-complete-refinement-94/verification/index.html','research/experiments/miniplayer-complete-refinement-94/highlight/index.html']:
 assert b'<html' in get(path)
r={'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deployed_commit':expected,'url':URL+'miniplayer-refinement.html','report_and_stage_pages':True,'all_64_png_hashes_exact':True,'assets':assets}
(BASE/'verification/live-publication.json').write_text(json.dumps(r,indent=2)+'\n');print('LIVE VERIFIED',expected,len(assets))
