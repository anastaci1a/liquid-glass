"""Format retained numerical evidence only; no geometry, rays or metrics run."""
from pathlib import Path
import json,hashlib,shutil,html
import numpy as np
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).parent;ROOT=OUT.parents[2];old=OUT/'as-run-crops';old.mkdir(exist_ok=False);font=ImageFont.load_default(size=16);corrections=[]
P=json.loads((ROOT/'research/experiments/miniplayer-inverse-forward-18/protocol.json').read_text());F=json.loads((ROOT/'reconstruction/families/music-mini-player-working.json').read_text());L=F['length_unit_native_pixels'];sections=np.load(OUT/'actual-sections.npz');rayrows=[];parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="750" viewBox="0 0 1000 750"><rect width="1000" height="750" fill="white"/><g font-family="sans-serif" font-size="13" fill="black"><text x="20" y="24">Actual power-eight front, unchanged inverse back and retained native rays</text><text x="20" y="45">Coordinates in original L; 1 L = 88.5 native pixels. Both axes use equal scale in each panel.</text>']
for mi,member in enumerate(['expanded','compact']):
 crops=P['fixed_crops'][member]
 for k in ['a','b']:
  file=OUT/f'{member}-{k}-crops.png';shutil.copy2(file,old/file.name);im=Image.open(file).convert('RGB');before=np.array(im);mask=np.ones(before.shape[:2],bool);y=0
  for name,(a,b,c,d) in crops.items():
   w,h=2*(c-a),2*(d-b);header=Image.new('RGB',(im.width,32),'white');draw=ImageDraw.Draw(header)
   for i,label in enumerate(['Ref','Working','Front 8']):draw.text((i*(w+2)+3,6),label,font=font,fill='black')
   im.paste(header,(0,y));mask[y:y+32]=False;y+=h+32+8
  assert np.array_equal(before[mask],np.array(im)[mask]);im.save(file);corrections.append({'file':file.name,'body_pixels_exact':True,'original_sha256':hashlib.sha256((old/file.name).read_bytes()).hexdigest(),'formatted_sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01');case=json.loads((work/'a/case.json').read_text());center=np.array(json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])
 if member=='compact':
  pose=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=np.array(case['center'])+L*np.array([pose['shape_dx'],pose['shape_dy']])
 q=np.load(OUT/f'{member}-paths.npz');a=F['members'][member]['major_half'];r=F['geometry']['corner_radius'];x0,y0,x1,y1=case['crop'];iy=round(2*(center[1]-y0+.25));selected=[]
 for desired in [-a+.01*r,-.5*a,0.,.5*a,a-.01*r]:
  ix=round(2*(center[0]+desired*L-x0+.25));assert q['complete'][iy,ix] and q['inside'][iy,ix];entry=q['front'][iy,ix];back=q['back'][iy,ix];source=np.array([q['X'][iy,ix],q['Y'][iy,ix],-F['optics']['background_distance']]);row={'member':member,'row':iy,'column':ix,'entry':entry.tolist(),'back':back.tolist(),'source':source.tolist(),'front_reflection_direction':q['front_reflection_direction'][iy,ix].tolist(),'projection':'x-z; actual transverse y values retained, not forced to zero'};selected.append(row);rayrows.append(row)
 top=80+mi*330;parts.append(f'<text x="20" y="{top}">{member}: longitudinal section and x-z projected actual native paths</text>');scale=900/(2*a+1);cx=500;zbase=top+45
 def xy(x,z):return (cx+scale*x,zbase-scale*z)
 for col,color in [(2,'#1763c3'),(3,'#bd5b18')]:
  s=sections[f'{member}_x'];points=' '.join(f'{xx:.5f},{zz:.5f}' for xx,zz in [xy(x,z) for x,z in zip(s[:,0],s[:,col])]);parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{points}"/>')
 for row in selected:
  pts=[row['entry'],row['back'],row['source']];points=' '.join(f'{xx:.5f},{zz:.5f}' for xx,zz in [xy(p[0],p[2]) for p in pts]);parts.append(f'<polyline fill="none" stroke="#444" stroke-width="1" points="{points}"/>')
 left,zz=xy(-a-.3,-F['optics']['background_distance']);right,_=xy(a+.3,-F['optics']['background_distance']);parts.append(f'<line x1="{left}" x2="{right}" y1="{zz}" y2="{zz}" stroke="#aaa" stroke-dasharray="4,3"/><text x="20" y="{top+220}">Blue: actual front. Orange: actual back. Gray: retained primary paths. Dashed: background plane.</text>')
 # Transverse section at equal horizontal/vertical scale, drawn from retained values.
 s=sections[f'{member}_y'];sc=150;xc=800;zb=top+265;parts.append(f'<text x="20" y="{top+270}">Transverse section: equal axes; no independent lens drawing.</text>')
 for col,color in [(2,'#1763c3'),(3,'#bd5b18')]:
  points=' '.join(f'{xc+sc*y:.5f},{zb-sc*z:.5f}' for y,z in zip(s[:,1],s[:,col]));parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{points}"/>')
parts.append('</g></svg>');(OUT/'actual-sections-rays.svg').write_text(''.join(parts));(OUT/'presentation.json').write_text(json.dumps({'scope':'Retained values only; no optical calculation, source sample or metric replay. Crop captions shortened without changing any body pixel. Row order follows original lower_right_rim, upper_left_rim, left_cap, body.', 'caption_checks':corrections,'selected_actual_native_paths':rayrows,'section_file':'actual-sections.npz','original_length_native_pixels':L},indent=2)+'\n')
