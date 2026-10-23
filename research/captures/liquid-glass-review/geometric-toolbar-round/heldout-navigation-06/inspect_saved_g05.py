"""Independent saved-artifact/source-address review. NO geometry tracing/RGB sampling."""
from pathlib import Path
import json,hashlib
import numpy as np
P=Path('/evidence/extended/geometric-playback-inferred');O=Path('/evidence/extended/geometric-toolbar-round/heldout-navigation-06')
proof=json.loads((P/'source-proof-FIRST.json').read_text());A=np.vstack([proof['source_registration']['matrix'],[0,0,1]]);inv=np.linalg.inv(A)
r={'scope':'Read SAVED queries/proof/profile only; ZERO retrace/rerender/RGB sampling','hashes':{},'query_files':0,'cached_addresses':0,'nonfinite':0,'unsupported_bilinear':0,'unsupported_registered_frame_texels':0,'bounds':[1e30,1e30,-1e30,-1e30]}
for name,digest in proof['source_hashes'].items():
 path=Path('/evidence/apple-matches/public-settled-replay')/name;actual=hashlib.sha256(path.read_bytes()).hexdigest();r['hashes'][name]={'expected':digest,'actual':actual,'match':actual==digest};assert actual==digest
for path in sorted((P/'queries').glob('*.npz')):
 q=np.load(path);X,Y=q['X'],q['Y'];r['query_files']+=1;r['cached_addresses']+=X.size;r['nonfinite']+=int((~np.isfinite(X)|~np.isfinite(Y)).sum());assert np.isfinite(X).all() and np.isfinite(Y).all()
 x=np.floor(X).astype(int);y=np.floor(Y).astype(int);r['unsupported_bilinear']+=int(((x<0)|(y<0)|(x+1>=1920)|(y+1>=1080)).sum())
 for ix,iy in [(0,0),(1,0),(0,1),(1,1)]:
  u=inv[0,0]*(x+ix)+inv[0,1]*(y+iy)+inv[0,2];v=inv[1,0]*(x+ix)+inv[1,1]*(y+iy)+inv[1,2]
  r['unsupported_registered_frame_texels']+=int(((u<0)|(v<0)|(u>=1919)|(v>=1079)).sum())
 b=r['bounds'];r['bounds']=[min(b[0],float(X.min())),min(b[1],float(Y.min())),max(b[2],float(X.max())),max(b[3],float(Y.max()))]
assert r['cached_addresses']==proof['all_crop_rays'] and r['unsupported_bilinear']==r['unsupported_registered_frame_texels']==r['nonfinite']==0
assert r['bounds']==proof['source_query_bounds']
rad=np.load(P/'radial-geometry.npz');old=np.load('/evidence/extended/geometric-playback-inverse/geometry-513.npz');r['saved_radial_paths_complete']=bool(rad['complete'].all());r['saved_G02_source_r_difference']=float(abs(rad['X']-old['source_r']).max());assert r['saved_G02_source_r_difference']==0
r['saved_radial_min_map_derivative']=float(np.gradient(rad['X'],rad['r']).min())
r['core_sha256']=hashlib.sha256((P/'code/geometric_optics.py').read_bytes()).hexdigest();r['proof_sha256']=hashlib.sha256((P/'source-proof-FIRST.json').read_bytes()).hexdigest();r['saved_images']={name:hashlib.sha256((P/name).read_bytes()).hexdigest() for name in ['comparison.png','rim-crops.png']};r['status']='PASS_SAVED_SOURCE_PROOF_AND_MAP_IDENTITY_NOT_FIDELITY'
(O/'g05-peer-cached-audit.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
