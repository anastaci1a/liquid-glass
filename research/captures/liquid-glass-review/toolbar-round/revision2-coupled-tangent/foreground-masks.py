import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-evidence-package/code')
import numpy as np
from vector_foreground import _coverage
p=Path('/tmp/agent-toolbar-evidence-package');q=json.loads((p/'recipe.json').read_text());case=q['case'];arrays={};meta=[]
for layer in q['foreground_layers']:
    raw=(p/'inputs'/layer['asset']).read_bytes();assert hashlib.sha256(raw).hexdigest()==layer['sha256']
    arrays[layer['name']]=_coverage(raw,tuple(case['crop']),tuple(layer['placement']),1)
    meta.append({'name':layer['name'],'asset_sha256':layer['sha256'],'shape':list(arrays[layer['name']].shape),'box':layer['box'],'color':layer['color']})
np.savez('/tmp/agent-toolbar-evidence-package/derived-foreground.npz',**arrays);(p/'derived-foreground-metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))
