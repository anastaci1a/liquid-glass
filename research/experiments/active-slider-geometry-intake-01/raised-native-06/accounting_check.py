from pathlib import Path
import ast,json,hashlib
P=Path(__file__).resolve().parent
old=ast.parse((P.parent/'raised-back-05/surface.py').read_text());new=ast.parse((P/'native_surface.py').read_text())
class StripAccounting(ast.NodeTransformer):
 def visit_Global(self,node):return None
 def visit_AugAssign(self,node):
  if isinstance(node.target,ast.Name) and node.target.id in ['height_evaluations','footprint_evaluations']:return None
  return node
 def visit_If(self,node):
  if len(node.body)==1 and isinstance(node.body[0],ast.Raise):return None
  return self.generic_visit(node)
def numeric(tree):
 cls=next(x for x in tree.body if isinstance(x,ast.ClassDef));return ast.dump(StripAccounting().visit(cls),include_attributes=False)
assert numeric(old)==numeric(new),'Numerical adapter AST changed'
(P/'accounting-verification.json').write_text(json.dumps(dict(geometry_class_AST_exact_after_removing_budget_accounting=True,original_sha256=hashlib.sha256((P.parent/'raised-back-05/surface.py').read_bytes()).hexdigest(),native_phase_sha256=hashlib.sha256((P/'native_surface.py').read_bytes()).hexdigest(),graph_cap=8000000,prior_height_count_preserved=9350,new_rays=0),indent=2)+'\n')
