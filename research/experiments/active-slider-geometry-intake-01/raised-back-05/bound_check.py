"""Evaluate the declared global bound first; stop on failure without sampling."""
from pathlib import Path
import sys,json,datetime,time,hashlib,os
P=Path(__file__).resolve().parent;ROOT=P.parent;R=ROOT.parents[2]
sys.path.insert(0,str(R/'reconstruction'))
from crowned_bevel import CrownedBevel
os.umask(0o002)
proto=json.loads((P/'protocol.json').read_text());end=datetime.datetime.fromisoformat(proto['deadline_utc'].replace('Z','+00:00')).timestamp();assert time.time()<end and not (P/'result.json').exists()
proposal=json.loads((ROOT/'proposal.json').read_text())
for row in proposal['code']:assert hashlib.sha256((R/row['file']).read_bytes()).hexdigest()==row['sha256'],row['file']
rows=[]
for case in proposal['cases']:
 a,b=case['corrected_half_over_L'];base=CrownedBevel((a,b),.15,.08);rho=base.rho_gradient_bound;first=.88*rho;second=.8/a;M=max(first,second);critical=1/(1.5**2-1)**.5;criterion=(1.5**2-1)*M*M
 rows.append(dict(case=case['key'],half=[a,b],rho_gradient_bound=rho,h1_slope_bound=first,h2_slope_bound=second,prescribed_M=M,critical_slope=critical,subcritical_measure=criterion,strict_subcritical=criterion<1,maximum_h1=.121,harmonic_height_bound=.121*.4/(.121+.4),minimum_background_clearance=2-.121*.4/(.121+.4)))
assert time.time()<end
status='STOP_PRESCRIBED_GLOBAL_BOUND_NOT_SUBCRITICAL' if not all(r['strict_subcritical'] for r in rows) else 'BOUND_PASSES_REQUIRES_REMAINING_GEOMETRY_CONTROLS'
result=dict(status=status,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,new_fixture_comparator_rays=0,new_height_evaluations=0,footprint_endpoint_derivative_evaluations=2,new_native_rays=0,RGB_queries=0,images=0,fits=0,cumulative_fixture_comparator_rays=8182,cumulative_native_rays=7473600,cumulative_images=4,limits='Failure of this prescribed sufficient bound is not observed TIR, a failed actual ray or proof that a sharper certificate is impossible. No bound tightening or tuning attempted.')
(P/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
