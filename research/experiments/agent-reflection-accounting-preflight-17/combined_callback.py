"""Proposed accounting only. No shared model import or numerical evaluation."""
import math
from numbers import Real
SCHEMA={}
def add(owner,names,rule,category):
 for name in names.split():SCHEMA[(owner,name)]=(rule,category)
add(None,'trace_flat_front_orthographic trace_closed_orthographic','xy','interface')
add('ScaledFlatBack','__init__ maximum_height slope_bound','scalar','scalar_bounds')
add('ScaledFlatBack','height_gradient boundary_mask','xy','point_queries')
add('HarmonicCircularBack','__init__ __post_init__ maximum_height slope_bound','scalar','scalar_bounds')
add('HarmonicCircularBack','height_gradient boundary_mask','xy','point_queries')
add(None,'bevel_profile','rho','point_queries')
add(None,'harmonic_cap','harmonic_pair','point_queries')
add(None,'refract','vector_pair','interface')
add(None,'reflect_direction','reflection_pair','interface')
add(None,'fresnel_components','fresnel_rows','interface')
add('CircularHeightSolid','__init__','scalar','scalar_bounds')
add('CircularHeightSolid','_height_gradient front_height boundary_mask','xy','point_queries')
add('CircularHeightSolid','level_gradient','points','closed_level')
add('CircularHeightSolid','nonsmooth_mask','points_uncertainty','point_queries')
add(None,'next_convex_boundary','segment_pair','interface')
add(None,'<lambda>','metadata','metadata_reshape')

class Counter:
 def __init__(self,shared_file,adapter_file,global_cap=100000,level_cap=50000,config_cap=15000,config_level_cap=2000):
  self.shared_file=shared_file;self.adapter_file=adapter_file
  self.global_cap=global_cap;self.level_cap=level_cap;self.config_cap=config_cap;self.config_level_cap=config_level_cap
  self.ledger={'total':0,'closed_level_subset':0,'categories':{},'functions':{}}
  self.start_total=0;self.start_level=0
 def reserve_config(self):
  if self.ledger['total']+self.config_cap>self.global_cap or self.ledger['closed_level_subset']+self.config_level_cap>self.level_cap:raise RuntimeError('Cannot reserve complete configuration')
  self.start_total=self.ledger['total'];self.start_level=self.ledger['closed_level_subset']
 @staticmethod
 def shape(value):
  shape=tuple(getattr(value,'shape',()))
  if len(shape) not in (1,2) or not 1<=shape[0]<=33 or (len(shape)==2 and shape[1]!=3):raise ValueError('Unsupported fixture shape')
  return shape
 @classmethod
 def matching(cls,left,right,rank):
  a=cls.shape(left);b=cls.shape(right)
  if a!=b or len(a)!=rank:raise ValueError('Matched fixture shapes required; broadcasting is not supported')
  return a[0]
 def __call__(self,frame,event,arg=None):
  if event!='call':return
  code=frame.f_code;v=frame.f_locals;owner=type(v['self']).__name__ if 'self' in v else None
  generated=code.co_filename=='<string>' and owner=='HarmonicCircularBack'
  if code.co_filename not in (self.shared_file,self.adapter_file) and not generated:return
  if generated and code.co_name!='__init__':raise RuntimeError('Undeclared generated method')
  # Only selected adapter methods belong to adapter scope; harness functions are ignored.
  if code.co_filename==self.adapter_file and owner!='ScaledFlatBack':return
  key=(owner,code.co_name)
  if key not in SCHEMA:raise RuntimeError('Undeclared selected shared call: '+str(key))
  rule,category=SCHEMA[key]
  if rule=='scalar':n=1
  elif rule=='xy':n=self.matching(v['x'],v['y'],1)
  elif rule=='rho':
   s=self.shape(v['rho'])
   if len(s)!=1:raise ValueError('rho must be one-dimensional')
   n=s[0]
  elif rule=='harmonic_pair':n=self.matching(v['first'],v['second'],1)
  elif rule=='vector_pair':n=self.matching(v['incident'],v['against_incident_normal'],2)
  elif rule=='reflection_pair':
   n=self.matching(v['incident'],v['outward_normal'],2)
   if n>16:raise ValueError('Reflection batches require1..16 rows')
  elif rule=='fresnel_rows':
   shape=self.shape(v['cosine'])
   if len(shape)!=1 or shape[0]>16:raise ValueError('Fresnel batches require1..16 cosine rows')
   for index in (v['n_from'],v['n_to']):
    if not isinstance(index,Real) or isinstance(index,bool) or tuple(getattr(index,'shape',())) or not math.isfinite(float(index)) or index<=0:raise ValueError('Finite positive real scalar indices required')
   n=shape[0]
  elif rule=='segment_pair':n=self.matching(v['points'],v['directions'],2)
  elif rule in ('points','points_uncertainty'):
   s=self.shape(v['p'])
   if len(s)!=2:raise ValueError('Point rows must have three components')
   n=s[0]
   if rule=='points_uncertainty' and self.shape(v['uncertainty'])!=(n,):raise ValueError('Bracket rows must match')
  elif rule=='metadata':
   if code.co_qualname!='trace_closed_orthographic.<locals>.<lambda>':raise RuntimeError('Undeclared metadata lambda')
   s=self.shape(v['v']);n=s[0]
   if tuple(v['shape'])!=(n,):raise ValueError('Metadata output shape must match fixture rows')
  else:raise RuntimeError('Unknown schema rule')
  level=n if category=='closed_level' else 0
  # All rejection checks precede every mutation, including categories and per-function counts.
  if self.ledger['total']+n>self.global_cap:raise RuntimeError('Global nested cap')
  if self.ledger['total']+n-self.start_total>self.config_cap:raise RuntimeError('Configuration nested cap')
  if self.ledger['closed_level_subset']+level>self.level_cap:raise RuntimeError('Global level cap')
  if self.ledger['closed_level_subset']+level-self.start_level>self.config_level_cap:raise RuntimeError('Configuration level cap')
  self.ledger['total']+=n;self.ledger['closed_level_subset']+=level
  self.ledger['categories'][category]=self.ledger['categories'].get(category,0)+n
  label=(owner+'.' if owner else '')+code.co_name
  self.ledger['functions'][label]=self.ledger['functions'].get(label,0)+n
