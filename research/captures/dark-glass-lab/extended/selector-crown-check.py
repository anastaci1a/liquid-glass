import sys,json,types,subprocess
from pathlib import Path
import numpy as np
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from extended_fit import Study
old=types.ModuleType('before_crown');exec(Path('/evidence/extended/extended-fit-before-crown.py').read_text(),old.__dict__)
f=Path('/evidence/extended/active-segmented-selector');p=json.loads((f/'accepted.json').read_text())['parameters']
A=Study(f);B=old.Study(f);rng=np.random.default_rng(222);x=rng.uniform(-2.49,2.49,1000);y=rng.uniform(-.99,.99,1000)
for q in [p,{**p,'crown_softness':0}]:
 for actual,expected in zip(A.geometry_field(x,y,q),B.geometry_field(x,y,p)):np.testing.assert_array_equal(actual,expected)
print('PASS absent/zero crown reproduces previous geometry exactly at1000 points')
