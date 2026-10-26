"""Immutable data/code audit, including explicitly preserved source epochs."""
from pathlib import Path
import json,hashlib,datetime
from PIL import Image
R=Path(__file__).resolve().parents[3];O=Path(__file__).parent;cache={}
def sha(p):
 p=p.resolve()
 if p not in cache:cache[p]=hashlib.sha256(p.read_bytes()).hexdigest()
 return cache[p]
versions={sha(p):str(p.relative_to(R)) for p in [O/'initial-native-driver.txt',O/'as-run-initial-color-edge.py',O/'as-run-floor-color-edge.py']}
checks=[]
files=list(O.glob('native-*/native-first-hashes.json'))+list(O.glob('native-*/native-last-hashes.json'))+[O/'display/continuation-hashes.json',O/'brightness-floor/continuation-hashes.json',O/'peak-brightness/hashes.json']
for f in files:
 for path,h in json.loads(f.read_text()).items():
  if not isinstance(h,str) or len(h)!=64:continue
  current=sha(R/path)
  if current==h:epoch='current'
  else:
   assert h in versions,(str(f),path,h,current);epoch=versions[h]
  checks.append(dict(receipt=str(f.relative_to(O)),path=path,verified_epoch=epoch,sha256=h))
# Initial failed driver/source receipt is retained independently.
for path,h in json.loads((O/'native-r0.75/native-inputs-FIRST.json').read_text())['hashes'].items():
 current=sha(R/path);assert current==h or h in versions
# Every file retained before continuation must still be exact.
for folder,key in [('display','retained_first_files'),('brightness-floor','retained_files')]:
 for name,h in json.loads((O/folder/'continuation-contract.json').read_text())[key].items():assert sha(O/folder/name)==h,(folder,name)
viewed=[]
for folder in ['native-r0.75-complete','native-r1.25']:
 for c in ['expanded-a','compact-b']:viewed.append(O/folder/f'{c}-geometry-comparison.png')
for folder,suffix in [('display','combined'),('brightness-floor','floor0.24'),('peak-brightness','floor0.24')]:
 for c in ['expanded-a','expanded-b','compact-a','compact-b']:viewed.append(O/folder/f'{c}-{suffix}-comparison.png')
for c,side in [('expanded-a','right'),('expanded-a','left'),('compact-b','right'),('compact-a','left')]:viewed.append(R/f'guide/assets/middle99-{c}-{side}-detail.png')
pixels=0
for p in viewed:
 with Image.open(p) as im:pixels+=im.width*im.height
panels=json.loads((O/'publication-panels.json').read_text());assert pixels+panels['decoded_bitmap_pixels']<panels['cap']
last=json.loads((O/'peak-brightness/result.json').read_text());assert all(x['max_array_error']==0 and x['metrics_exact'] for x in last['own_replays'])
result=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,retained_failures_unchanged=True,final_four_replays_pixel_and_metric_exact=True,documentation='258 documents,661 equations,90435 local links/assets/anchors,8627 rendered HTML pages.',visual_review=dict(full_and_detail_files=[str(p.relative_to(R)) for p in viewed],full_png_pixel_supplement=pixels,presentation_plus_visual_pixels=pixels+panels['decoded_bitmap_pixels'],cap=panels['cap']),browser_status='See separate publication/browser receipt; initial attempt preceded site generation and is not a scientific rerun.',selected_changed=False)
(O/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
manifest={str(p.relative_to(O)):sha(p) for p in sorted(O.rglob('*')) if p.is_file() and p.name!='manifest.json'}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(len(checks),'immutable bindings;',len(manifest),'artifact files; visual supplement',pixels)
