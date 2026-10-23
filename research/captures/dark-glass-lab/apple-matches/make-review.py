import sys
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from publish import read,compose,pair,CASES
f=Path('/evidence/apple-matches/curvature-contour');out=Path('/review')
items=[('regular','tensor','01-toolbar-current.png','Current tensor image map'),('slider','chromatic','03-slider-current.png','Measured outline / chromatic image map'),('media','exponential','04-playback-smooth-crown.png','Smooth-front / flat-exit comparator')]
for name,model,dest,label in items:
 target=read(f/f'{name}-target.png');material=read(f/f'{name}-{model}.png');full=compose(name,CASES[name],target,material,f);x0,y0,x1,y1=CASES[name]['crop']
 pair(target[y0:y1,x0:x1],full[y0:y1,x0:x1],('Apple reference',label),font_size=16).save(out/dest)
 if name=='regular':pair(target[369:435,650:1270],full[369:435,650:1270],('Apple upper rim','Current tensor image map'),font_size=16).save(out/'02-toolbar-upper-rim.png')
