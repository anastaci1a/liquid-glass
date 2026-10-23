import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from PIL import Image
import toolbar_candidate as base
from reproduce import CASES
root=Path('/tmp/agent-toolbar-run');settled=Path('/tmp/agent-toolbar-inner-settlement');q=json.loads((settled/'recipe.json').read_text());flat=copy.deepcopy(q);change=flat.pop('supported_transition');assert change['mode']=='inner'
for i,v in zip([4,5,6],change['normal_delta']):flat['parameters']['coefficients'][i]+=v
source=np.asarray(Image.open(root/'source.png')).astype(float)/255;C,a=base.render(source,CASES['regular'],flat);delta=float(np.max(np.abs(C-np.load(settled/'material.npy'))));assert delta==0,delta
(settled/'candidate-flat-recipe.json').write_text(json.dumps(flat,indent=2)+'\n');(settled/'flat-recipe-verification.json').write_text(json.dumps({'native_material_max_absolute_difference':delta,'new_model_primitive_required':False,'changed_only_existing_normal_coefficients':[4,5,6],'outer_coefficients_0_3_unchanged':True,'counted_passes':0},indent=2)+'\n');print('FLAT_RECIPE_EXACT',delta,flat['parameters']['coefficients'])
