"""Verify certificate documentation changes no executable transport code."""
from pathlib import Path
import ast,datetime,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;path='reconstruction/geometric_optics.py';before=subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT);after=(ROOT/path).read_bytes()
def executable(raw):
 t=ast.parse(raw)
 for n in ast.walk(t):
  if isinstance(n,(ast.Module,ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and n.body and isinstance(n.body[0],ast.Expr) and isinstance(n.body[0].value,ast.Constant) and isinstance(n.body[0].value.value,str):n.body.pop(0)
 return ast.dump(t,include_attributes=False)
assert executable(before)==executable(after)
p=json.loads((OUT/'protocol.json').read_text());now=datetime.datetime.now(datetime.timezone.utc);assert now<datetime.datetime.fromisoformat(p['deadline'])
(OUT/'code-verification.json').write_text(json.dumps(dict(executable_AST_exact=True,before_sha256=hashlib.sha256(before).hexdigest(),after_sha256=hashlib.sha256(after).hexdigest(),scope='Docstrings only; no changed numerical trace expressions or API return fields.',verified_at=now.isoformat()),indent=2)+'\n')
