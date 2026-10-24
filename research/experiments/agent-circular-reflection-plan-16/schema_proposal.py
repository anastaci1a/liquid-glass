"""Two accounting-only additions. No shared import or optical implementation."""
SCHEMA_ADDITIONS={
 'reflect_direction':{'arguments':['incident','outward_normal'],'unit':'matched N-by-3 vector rows','category':'interface'},
 'fresnel_components':{'arguments':['cosine','n_from','n_to'],'unit':'N cosine rows; scalar indices','category':'interface'},
}
def count_new_delegate(frame):
 name=frame.f_code.co_name;v=frame.f_locals
 if name not in SCHEMA_ADDITIONS:raise RuntimeError('Undeclared new delegate')
 if name=='reflect_direction':
  a=tuple(v['incident'].shape);b=tuple(v['outward_normal'].shape)
  if a!=b or len(a)!=2 or a[1]!=3 or not 1<=a[0]<=16:raise ValueError('Matched vector rows required')
  return a[0]
 shape=tuple(getattr(v['cosine'],'shape',()))
 if len(shape)!=1 or not 1<=shape[0]<=16 or tuple(getattr(v['n_from'],'shape',())) or tuple(getattr(v['n_to'],'shape',())):raise ValueError('Cosine rows and scalar indices required')
 return shape[0]
def charge_synthetic(frame,ledger,limit):
 n=count_new_delegate(frame)
 if ledger['interface']+n>limit:raise RuntimeError('Pre-mutation interface cap')
 ledger['interface']+=n
 return n
