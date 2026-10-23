import sys,os,json,re,hashlib,copy
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from fontTools.svgLib.path import parse_path
from fontTools.pens.boundsPen import BoundsPen
R=Path('/evidence/extended/helper-toolbar-work/safari-magnifier-round');F=R/'foreground-control';sys.path.insert(0,str(R/'code'));os.umask(0o002);cv2.setNumThreads(1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(F/n).write_text(json.dumps(v,indent=2)+'\n')
assert not (F/'verification.json').exists()
raw=(F/'sfMagnifyingglass.js').read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest();assert blob=='4dd50231bc3adadeb15419d0fe663c78c76bcfce'
text=raw.decode();paths=re.findall(r'\{d:"([^"]+)"',text);assert len(paths)==1 and re.fullmatch(r'[MmLlHhVvCcSsQqTtAaZz0-9., +\-Ee]+',paths[0]);pen=BoundsPen(None);parse_path(paths[0],pen);l,b,r,t=pen.bounds;ink_bounds=[l,b,r,t];side=max(r-l,t-b);tx=-l+(side-(r-l))/2;ty=-b+(side-(t-b))/2
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {side:.12g} {side:.12g}"><path fill="#000" transform="translate({tx:.12g} {ty:.12g})" d="{paths[0]}"/></svg>\n';(F/'search-original-candidate.svg').write_text(svg)
from extended_fit import Study
from vector_revision import composite
s=Study(R/'a');old=np.load(R/'baseline-native-arrays.npz');rec=json.loads((R/'baseline-recipe.json').read_text());M=old['material'];baseline=old['complete'];layer=copy.deepcopy(s.case['foreground_layers'][0]);layer['vector_asset']='search-original-candidate.svg';layer['vector_sha256']=sha(F/'search-original-candidate.svg');shutil=None
# Coverage resolver reads folder; in-memory candidate only, frozen a/ files never edited.
s.folder=F;s.case=copy.deepcopy(s.case);s.case['foreground_layers']=[layer];s.vector_layers={tuple(layer['box']):layer};candidate=composite(s,rec['parameters'],M)
fg=old['glyph_mask'];err=(candidate-s.target_crop)*255;before=float(np.sqrt(np.mean(((baseline-s.target_crop)[fg]*255)**2)));after=float(np.sqrt(np.mean(err[fg]**2)));outside=~fg;assert np.array_equal(candidate[outside],baseline[outside]);np.savez_compressed(F/'candidate-native.npz',complete=candidate,unchanged_material=M,alpha=old['alpha']);Image.fromarray(np.uint8(np.rint(np.clip(candidate,0,1)*255))).save(F/'candidate-native.png')
# Fixed crop/placement, no position/weight/opacity fit; entire foreground guard is compared.
a,b,c,d=layer['box'];x0,y0,_,_=s.crop;ims=[s.target_crop[b-y0:d-y0,a-x0:c-x0],baseline[b-y0:d-y0,a-x0:c-x0],candidate[b-y0:d-y0,a-x0:c-x0]];out=Image.new('RGB',(468,222),'#222');dr=ImageDraw.Draw(out)
for i,(im,label) in enumerate(zip(ims,['Original','Canonical trace','External path'])):out.paste(Image.fromarray(np.uint8(np.rint(np.clip(im,0,1)*255))).resize((156,158),Image.Resampling.NEAREST),(156*i,64));dr.text((156*i+4,20),label,fill='white')
out.save(F/'foreground-comparison.png');result=dict(one_candidate=True,js_executed=False,pinned_commit='2a0100e93e11a22ea0ff5e0530efd10e2cf0d243',blob_sha1=blob,module_sha256=sha(F/'sfMagnifyingglass.js'),candidate_svg_sha256=sha(F/'search-original-candidate.svg'),ink_bounds=ink_bounds,shape='Exactly extracted literal Bezier path; ink bounding square centered preserving aspect, no target fitting',library_fillOpacity_085='NOT adopted; keep fixed black opacity1 as required',provenance='Third-party SF Symbols data export; authenticity to this pinned package verified, not independent proof of Apple official SVG identity or this Safari weight.',unchanged_placement=layer['vector_box'],unchanged_glyph_box=layer['box'],foreground_rmse_before=before,foreground_rmse_after=after,foreground_improved=after<before,outside_foreground_pixel_exact=True,material_reused_bit_exact=True,optical_render_count=0,fit_count=0,source_adopted=False,count=0,decision='PROPOSE separate canonical vector baseline update before tonefit' if after<before else 'RETAIN existing canonical clean trace approximation; ONE external candidate rejected, no search')
save('verification.json',result);save('proposed-layer.json',layer);print(json.dumps(result),flush=True)
